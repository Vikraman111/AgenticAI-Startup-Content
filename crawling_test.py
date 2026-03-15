#!/usr/bin/env python3
"""
CRAWLING & EXTRACTION TEST
A standalone script to test `trafilatura` extraction on any list of URLs.
"""

import requests
import trafilatura
import time
import cloudscraper

def test_extraction(urls):
    print("\n" + "="*80)
    print("🕸️  CRAWLING TEST: Universal Extraction")
    print("="*80 + "\n")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    # Initialize a Cloudscraper designed to bypass anti-bot systems
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})

    for idx, url in enumerate(urls, 1):
        print(f"[{idx}/{len(urls)}] Fetching: {url[:60]}...")
        
        try:
            # 1. Fetch the raw HTML using the scraper
            response = scraper.get(url, headers=headers, timeout=12)
            
            if response.status_code != 200:
                print(f"   ❌ HTTP Error {response.status_code}: Could not fetch page.\n")
                continue
                
            # 2. Use Trafilatura's heuristic engine to find the main content
            content = trafilatura.extract(
                response.text, 
                include_comments=False, 
                include_tables=False
            )
            
            # 3. Display the results
            if content:
                print(f"   ✅ Success! Extracted {len(content)} characters.")
                print("   Preview of extracted text:")
                print("-" * 60)
                # Print just the first 300 characters for a preview
                preview = content[:300].replace('\n', ' ') + "..."
                print(f"   {preview}")
                print("-" * 60 + "\n")
            else:
                print("   ⚠️ Failure: Could not find main article content on this page.\n")
                
        except requests.exceptions.Timeout:
             print("   ⌛ Timeout: The server took too long to respond.\n")
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            
        # Be polite to servers, wait a second between requests
        time.sleep(1)

if __name__ == "__main__":
    # Add any URLs you want to test here!
    dummy_urls = [
        "https://medium.com/blog/how-to-turn-your-threads-bluesky-or-x-thread-into-a-medium-story-7c6ed8d5c109",
        "https://techcrunch.com/2026/03/13/not-built-right-the-first-time-musks-xai-is-starting-over-again-again/",
        "https://www.businessinsider.com/meta-weighing-major-layoffs-as-it-pours-billions-into-ai-2026-3",
        "https://www.businessinsider.com/backyard-pub-building-mistakes-regrets-2026-3"
    ]
    
    test_extraction(dummy_urls)
