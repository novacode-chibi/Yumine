# Manga Cover URL Fetching Guide

## Overview

This document explains how to fetch manga cover URLs from the Jikan API (MyAnimeList) for mangas in `list_scans_fr.json` that have empty `coverUrl` fields.

## The Problem

Out of 897 total mangas in the `list_scans_fr.json` file:
- **First 100 mangas**: 93 have empty `coverUrl` fields (7 already have covers)
- **Remaining mangas**: Most also need cover URLs

## Solution

### Option 1: Run the Script Locally (Recommended)

The GitHub Actions environment has restricted network access and cannot reach `api.jikan.moe`. To fetch the cover URLs, you need to run the script on your local machine or a server with internet access.

#### Steps:

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/novacode-chibi/Yumine.git
   cd Yumine
   ```

2. **Install required dependencies**:
   ```bash
   pip install requests
   ```

3. **Run the script**:
   ```bash
   # Fetch covers for first 100 mangas
   python3 fetch_manga_covers.py 100
   
   # Or for all mangas (will take ~15 minutes due to API rate limits)
   python3 fetch_manga_covers.py 897
   ```

4. **Review the output**:
   - The script creates `list_scans_fr_updated.json` with the fetched cover URLs
   - Review the file to ensure covers were fetched correctly

5. **Replace the original file** (after verification):
   ```bash
   cp list_scans_fr_updated.json list_scans_fr.json
   ```

6. **Commit and push**:
   ```bash
   git add list_scans_fr.json
   git commit -m "Add manga cover URLs from Jikan API"
   git push
   ```

### Option 2: Manual API Calls

If you prefer to do this manually or in smaller batches, you can use the Jikan API directly:

```bash
# Example for a single manga
curl "https://api.jikan.moe/v4/manga?q=Naruto&limit=1" | jq '.data[0].images.jpg.image_url'
```

## Script Features

The `fetch_manga_covers.py` script includes:

- ✅ **Rate limiting**: Respects Jikan API limits (1 request per second)
- ✅ **Error handling**: Handles network errors, rate limits, and missing data
- ✅ **Progress tracking**: Shows which manga is being processed
- ✅ **Retry logic**: Retries failed requests up to 3 times
- ✅ **Preservation**: Only updates empty `coverUrl` fields, preserves existing covers
- ✅ **Summary report**: Shows statistics at the end

## API Rate Limits

Jikan API (v4) has the following rate limits:
- **3 requests per second**
- **60 requests per minute**

The script is configured to make 1 request per second to stay well within these limits.

## Expected Processing Time

- **100 mangas**: ~90 seconds (93 API calls at 1 per second)
- **897 mangas**: ~15 minutes (assuming ~800+ need covers)

## Troubleshooting

### Connection Errors

If you get connection errors:
1. Check your internet connection
2. Verify `api.jikan.moe` is accessible: `ping api.jikan.moe`
3. Check if you're behind a firewall or proxy

### Rate Limit Errors

If you hit rate limits:
- The script automatically waits 60 seconds and retries
- If this persists, increase the delay between requests in the script

### No Results Found

Some mangas might not be found because:
- They're not in the MyAnimeList database
- The title in French doesn't match the English/Japanese title
- The manga is too obscure or new

For these cases, you may need to:
1. Search manually on MyAnimeList
2. Use alternative spellings or original titles
3. Find cover images from other sources

## Example Output

```
📖 Reading list_scans_fr.json...
📊 Total mangas in file: 897
🎯 Processing first 100 mangas...
🔍 Found 93 mangas with empty coverUrl in first 100

[2/100] Fetching cover for: 10 Years In Friend Zone
  ✅ Found: https://cdn.myanimelist.net/images/manga/1/234567.jpg

[3/100] Fetching cover for: 100 Demons of Love
  ❌ Not found

...

✅ Updated 85 manga cover URLs

📊 Summary:
  - Total mangas processed: 100
  - Mangas with empty coverUrl: 93
  - Cover URLs fetched: 85
  - Remaining empty: 8
```

## Alternative: GitHub Actions with Secrets

If you want to automate this in GitHub Actions, you would need to:
1. Ensure the runner has access to external APIs
2. Run this as a scheduled workflow
3. Commit the results automatically

However, this requires proper network configuration in the GitHub Actions environment.

## Contact

If you need help or have questions:
- Open an issue on the GitHub repository
- Contact the repository maintainer

---

**Note**: This process respects Jikan's API rate limits and terms of service. Please be considerate when using their free API.
