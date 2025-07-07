import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from urllib.parse import urlparse, parse_qs

# --- CONFIGURATION ---

# 1. Get Supabase credentials from environment variables (GitHub Secrets)
SUPABASE_URL = os.environ.get("https://szdmjqgigwhtxpegvhvy.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InN6ZG1qcWdpZ3dodHhwZWd2aHZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTE4NDU3NjMsImV4cCI6MjA2NzQyMTc2M30.BKE8L74n99b7q3FugUV7q5As3qCtCzAhuT0lm4rCz4g")


# 2. Define your job search criteria
SEARCH_QUERY = "software engineer"
LOCATION = "Syracuse, NY"

# 3. Define the target job sites
TARGET_SITES = [
    "jobs.lever.co",
    "boards.greenhouse.io",
    "wd1.myworkdayjobs.com",
    "jobs.bamboohr.com",
    "smartrecruiters.com"
]

# --- SCRIPT ---

def scrape_and_save_jobs():
    """
    Scrapes Google for new job postings from target sites and saves them to Supabase.
    """
    print("--- Starting Job Scraper ---")
    
    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Successfully connected to Supabase.")
    except Exception as e:
        print(f"❌ Could not connect to Supabase: {e}")
        return

    # Set headers to mimic a real browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    new_jobs_found = 0

    # Loop through each target site and perform a search
    for site in TARGET_SITES:
        search_term = f'"{SEARCH_QUERY}" "{LOCATION}" site:{site}'
        print(f"\n🔎 Searching for: {search_term}")
        
        google_url = f"https://www.google.com/search?q={search_term}&tbs=qdr:d" # qdr:d = last 24 hours
        
        try:
            response = requests.get(google_url, headers=headers)
            response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all the links in the search results
            links = soup.find_all('a')
            
            urls_to_check = []
            for link in links:
                href = link.get('href')
                if href and href.startswith('/url?q='):
                    # Extract the actual URL from Google's redirect link
                    clean_url = parse_qs(urlparse(href).query).get('q', [None])[0]
                    if clean_url and any(s in clean_url for s in TARGET_SITES):
                        urls_to_check.append(clean_url)
            
            if not urls_to_check:
                print("... No new job URLs found in search results.")
                continue

            # Check which of these URLs are new
            for url in set(urls_to_check): # Use set() to remove duplicate URLs
                try:
                    # Check if the URL already exists in our database
                    result = supabase.table('jobs').select('id').eq('url', url).execute()
                    
                    if not result.data:
                        # This is a new job, let's save it
                        print(f"  ➡️ Found new job: {url}")
                        job_data = {
                            "title": SEARCH_QUERY,
                            "company": urlparse(url).hostname,
                            "location": LOCATION,
                            "url": url,
                            "source": site
                        }
                        supabase.table('jobs').insert(job_data).execute()
                        new_jobs_found += 1
                    # else:
                        # print(f"  (Skipping existing job: {url})")

                except Exception as e:
                    # Ignore errors for single URLs (e.g., duplicates) and continue
                    if 'duplicate key value violates unique constraint' not in str(e):
                         print(f"  ❌ Error processing URL {url}: {e}")

        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed to fetch Google search results: {e}")

    print(f"\n--- Scraper Finished. Found and saved {new_jobs_found} new jobs. ---")

# --- RUN THE SCRIPT ---
if __name__ == "__main__":
    if SUPABASE_URL == "YOUR_SUPABASE_URL" or SUPABASE_KEY == "YOUR_SERVICE_ROLE_KEY":
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! ERROR: Please update SUPABASE_URL and SUPABASE_KEY in the script. !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        scrape_and_save_jobs()