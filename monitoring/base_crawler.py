import feedparser
import trafilatura
import requests
import hashlib
import time
from core.registry import Registry
from core.filter_logic import SmartFilter

class BaseCrawler:
    def __init__(self, name):
        self.name = name
        self.registry = Registry()
        self.filter = SmartFilter() # Now using LLM
        self.headers = {'User-Agent': 'Mozilla/5.0...'}

    def _generate_id(self, url):
        return hashlib.sha256(url.encode()).hexdigest()

    def process_feed(self, rss_url):
        print(f"\n📡 [{self.name}] Scanning: {rss_url}")
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                url = entry.link
                title = entry.title
                summary = entry.get('summary', '')

                if self.registry.exists(self._generate_id(url)):
                    continue

                # The LLM Gatekeeper
                is_relevant, _ = self.filter.is_relevant(title, summary)
                
                if is_relevant:
                    print(f"   ✅ MATCH: {title[:60]}...")
                    self._extract_and_save(url, title)
                else:
                    # Optional: print(f"   🗑️ Skipped: {title[:40]}")
                    continue

        except Exception as e:
            print(f"   ⚠️ Feed Error: {e}")

    def _extract_and_save(self, url, title):
        try:
            page = requests.get(url, headers=self.headers, timeout=10)
            content = trafilatura.extract(page.text, include_comments=False, include_tables=False)
            
            if content and len(content) > 300:
                self.registry.register_artifact(
                    url=url,
                    content=content,
                    source_module=self.name,
                    title=title
                )
                print(f"      💾 Saved to database.")
        except Exception as e:
            print(f"      ❌ Extraction Error: {e}")