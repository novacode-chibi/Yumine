#!/usr/bin/env python3
"""
Script to fetch manga cover URLs from Jikan API (MyAnimeList)
and update the list_scans_fr.json file.

This script should be run locally where you have internet access to api.jikan.moe

Usage:
    python3 fetch_manga_covers.py [number_of_mangas]
    
Examples:
    python3 fetch_manga_covers.py          # Process first 100 mangas
    python3 fetch_manga_covers.py 200      # Process first 200 mangas
"""

import requests
import json
import time
import sys
import urllib.parse

# Jikan API base URL
JIKAN_API_BASE = "https://api.jikan.moe/v4"

def search_manga_cover(manga_name, retry_count=0):
    """
    Search for a manga by name using Jikan API and return the cover URL.
    Returns the first result's cover URL or None if not found.
    
    Args:
        manga_name: Name of the manga to search for
        retry_count: Current retry attempt number
    
    Returns:
        Cover URL string or None if not found
    """
    max_retries = 3
    
    try:
        # URL encode the manga name for the API request
        encoded_name = urllib.parse.quote(manga_name)
        url = f"{JIKAN_API_BASE}/manga?q={encoded_name}&limit=1"
        
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('data') and len(data['data']) > 0:
                manga = data['data'][0]
                cover_url = manga.get('images', {}).get('jpg', {}).get('image_url', '')
                if cover_url:
                    return cover_url
        elif response.status_code == 429:
            # Rate limit hit, wait longer
            wait_time = 60
            print(f"  ⚠️ Rate limit hit, waiting {wait_time} seconds...")
            time.sleep(wait_time)
            if retry_count < max_retries:
                return search_manga_cover(manga_name, retry_count + 1)
        elif response.status_code == 404:
            print(f"  ❌ Not found in MyAnimeList database")
        else:
            print(f"  ⚠️ API error {response.status_code} for '{manga_name}'")
            
    except requests.exceptions.Timeout:
        print(f"  ⚠️ Request timeout for '{manga_name}'")
        if retry_count < max_retries:
            time.sleep(5)
            return search_manga_cover(manga_name, retry_count + 1)
    except requests.exceptions.ConnectionError as e:
        print(f"  ⚠️ Connection error: Cannot reach api.jikan.moe")
        print(f"     Please ensure you have internet access and the domain is not blocked.")
        if retry_count < max_retries:
            time.sleep(5)
            return search_manga_cover(manga_name, retry_count + 1)
    except Exception as e:
        print(f"  ⚠️ Unexpected error for '{manga_name}': {str(e)}")
    
    return None

def process_first_n_mangas(input_file, output_file, n=100):
    """
    Process the first N mangas from the input JSON file and fetch cover URLs
    for those with empty coverUrl fields.
    """
    # Read the original JSON file
    print(f"📖 Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    mangas = data.get('mangas', [])
    total_mangas = len(mangas)
    print(f"📊 Total mangas in file: {total_mangas}")
    
    # Process only the first N mangas
    mangas_to_process = mangas[:n]
    print(f"🎯 Processing first {n} mangas...")
    
    # Count how many need cover URLs
    empty_count = sum(1 for m in mangas_to_process if not m.get('coverUrl', ''))
    print(f"🔍 Found {empty_count} mangas with empty coverUrl in first {n}")
    
    # Fetch cover URLs for mangas with empty coverUrl
    updated_count = 0
    for i, manga in enumerate(mangas_to_process):
        manga_name = manga.get('name', '')
        current_cover = manga.get('coverUrl', '')
        
        # Skip if already has a cover URL
        if current_cover:
            continue
        
        print(f"\n[{i+1}/{n}] Fetching cover for: {manga_name}")
        
        # Fetch cover URL from Jikan API
        cover_url = search_manga_cover(manga_name)
        
        if cover_url:
            manga['coverUrl'] = cover_url
            updated_count += 1
            print(f"  ✅ Found: {cover_url}")
        else:
            print(f"  ❌ Not found")
        
        # Rate limiting: Jikan API allows 3 requests per second, 60 per minute
        # We'll be conservative and wait 1 second between requests
        time.sleep(1)
    
    print(f"\n✅ Updated {updated_count} manga cover URLs")
    
    # Update the data with processed mangas
    data['mangas'][:n] = mangas_to_process
    
    # Save the complete updated JSON
    print(f"\n💾 Saving updated JSON to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    
    print(f"✅ Done! Output saved to {output_file}")
    
    # Print summary
    print("\n" + "="*50)
    print("📊 Summary:")
    print(f"  - Total mangas processed: {n}")
    print(f"  - Mangas with empty coverUrl: {empty_count}")
    print(f"  - Cover URLs fetched: {updated_count}")
    print(f"  - Remaining empty: {empty_count - updated_count}")
    print("="*50)

if __name__ == "__main__":
    input_file = "list_scans_fr.json"
    output_file = "list_scans_fr_updated.json"
    n_mangas = 100
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        n_mangas = int(sys.argv[1])
    
    process_first_n_mangas(input_file, output_file, n_mangas)
