# Yumine — README

## 1. Aperçu

Petit projet Python contenant des scripts de scraping et des fichiers JSON de données d’anime.  
Objectif probable : récupérer et stocker des informations d’anime (catalogue / saisonniers) via des scripts (`scraper.py`, `fetch_anime.py`) et conserver le résultat dans `*.json`.  
([GitHub][1])

---

## 2. Arborescence importante (vue d’ensemble)

Fichiers et dossiers présents dans la racine (avec description inférée) :

* `.github/workflows/` — workflows GitHub Actions (automatisation). ([GitHub][1])
* `scraper.py` — script principal de scraping (probablement lance le crawl et écrit les JSON). ([GitHub][2])
* `fetch_anime.py` — module/helper pour récupérer/désérialiser une fiche anime ou appeler des endpoints. ([GitHub][3])
* `requirements.txt` — dépendances Python pour l’environnement. ([GitHub][4])
* `animes.json` — base de données locale d’animes (meta / catalogue complet). ([GitHub][1])
* `seasonal_animes.json` — liste/objets pour les animes saisonniers. ([GitHub][1])
* `news.txt` — notes/flux d’actualités ou logs manuels. ([GitHub][1])

---

## 3. Prérequis

* Python **3.10+** recommandé (≥ 3.8 devrait fonctionner)
* `virtualenv` / `venv`
* Accès réseau (pour que le scraper puisse interroger les sites)
* Dépendances listées dans `requirements.txt`. ([GitHub][4])

---

## 4. Installation rapide

```bash
# Cloner le repo
git clone https://github.com/novacode-chibi/Yumine.git
cd Yumine

# Créer un env virtuel
python -m venv .venv
source .venv/bin/activate   # mac/linux
# .venv\Scripts\activate    # windows

# Installer dépendances
pip install -r requirements.txt
