import json
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry

BASE_URL = "https://anime-sama.fr/catalogue?page="
OUTPUT_FILE = "animes.json"

# Configuration session avec retries
session = requests.Session()
retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
session.mount("https://", HTTPAdapter(max_retries=retries))
session.headers.update({
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
})


def fetch_html(page_number: int, timeout: int = 15) -> str:
    url = f"{BASE_URL}{page_number}"
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def parse_animes(html: str):
    soup = BeautifulSoup(html, "html.parser")
    found = []

    # Parcours des liens contenant un <h1> (titre) — on affine ensuite par la présence d'un marqueur "Anime"
    for a in soup.find_all("a", href=True):
        h1 = a.find("h1")
        if not h1:
            continue

        titre = h1.get_text(strip=True)
        if not titre:
            continue

        # remonter jusqu'à un conteneur proche pour vérifier s'il contient un paragraphe "Anime"
        parent = a
        is_anime_block = False
        for _ in range(4):  # on remonte max 4 niveaux
            if parent is None:
                break
            p = parent.find("p", string=lambda t: t and "Anime" in t)
            if p:
                is_anime_block = True
                break
            parent = parent.parent

        if not is_anime_block:
            # Certains templates affichent "Anime" ailleurs — on peut aussi chercher "Anime" dans le voisinage
            nearby_text = a.get_text(" ", strip=True)
            if "Anime" not in nearby_text:
                continue

        # Récupération lien et image (gère lazy-loads)
        lien = urljoin(BASE_URL, a["href"])
        img = a.find("img")
        image = ""
        if img:
            # prioriser les attributs courants pour lazy-loading
            image = img.get("data-src") or img.get("data-original") or img.get("data-lazy") or img.get("src") or ""
            image = image.strip()
            if image:
                image = urljoin(BASE_URL, image)

        found.append({"titre": titre, "lien": lien, "image": image})

    # Dé-duplication basique (par lien)
    unique = []
    seen = set()
    for item in found:
        if item["lien"] not in seen:
            seen.add(item["lien"])
            unique.append(item)

    return unique


def scrape(max_pages: int = 200, delay: float = 1.0):
    page = 1
    all_animes = []

    while page <= max_pages:
        print(f"[+] Scraping page {page}...")
        try:
            html = fetch_html(page)
        except requests.HTTPError as e:
            print(f"[!] Erreur HTTP pour la page {page}: {e}. Arrêt.")
            break
        except requests.RequestException as e:
            print(f"[!] Erreur réseau pour la page {page}: {e}. Réessaie plus tard ou arrête.")
            break

        page_animes = parse_animes(html)
        if not page_animes:
            print(f"[-] Aucune donnée trouvée à la page {page}. Fin du scraping.")
            break

        print(f"    -> {len(page_animes)} animes trouvés sur la page {page}.")
        all_animes.extend(page_animes)

        page += 1
        time.sleep(delay)  # politesse : attente entre requêtes

    # Sauvegarde, en supprimant doublons finaux (par lien)
    final = []
    seen = set()
    for item in all_animes:
        if item["lien"] not in seen:
            seen.add(item["lien"])
            final.append(item)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final, f, ensure_ascii=False, indent=2)

    print(f"[✓] Scraping terminé. {len(final)} animes sauvegardés dans '{OUTPUT_FILE}'.")


if __name__ == "__main__":
    scrape()
