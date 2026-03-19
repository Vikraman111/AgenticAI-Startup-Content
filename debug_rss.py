import feedparser
import requests

urls = [
    "https://www.inc.com/rss.xml",
    "https://hbr.org/rss",
    "https://www.forbes.com/business/feed/",
    "https://www.entrepreneur.com/latest.rss"
]

for url in urls:
    print(f"\nScanning: {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}, timeout=10)
        print(f"   Status: {response.status_code}")
        feed = feedparser.parse(response.text)
        print(f"   Entries found: {len(feed.entries)}")
        if feed.entries:
            print(f"   First Title: {feed.entries[0].title}")
    except Exception as e:
        print(f"   Error: {e}")
