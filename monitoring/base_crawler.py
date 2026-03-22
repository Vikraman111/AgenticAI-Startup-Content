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
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

    def _generate_id(self, url):
        return hashlib.sha256(url.encode()).hexdigest()

    def process_feed(self, rss_url):
        print(f"\n📡 [{self.name}] Scanning: {rss_url}")
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                url, title = entry.link, entry.title
                summary = entry.get('summary', '')

                # 1. DB CHECK (Zero cost)
                if self.registry.exists(self._generate_id(url)):
                    # Optional: print(f"   ⏩ Duplicate: {title[:50]}...")
                    continue

                # 2. SEMANTIC TITLE MATCH (Very Cheap Pass)
                # Lowered threshold to 0.28 based on diagnostic results
                strategic_score = self.filter.get_strategic_score(title)
                if strategic_score < 0.28:
                    print(f"   📈 Low Relevance ({int(strategic_score*100)}%): {title[:55]}...")
                    continue

                print(f"   👀 Potential: {title[:60]}...")

                # 3. SCRAPE & VALIDATE (Zero Token Cost)
                content = self._extract_content(url)
                if not content or len(content) < 300:
                    print(f"      ⏭️  Skipped: Content too short ({len(content) if content else 0} chars)")
                    continue

                # 4. FINAL AI VALIDATION (High Intelligence)
                is_relevant, confidence = self.filter.is_relevant(title, content[:500])
                
                if is_relevant:
                    print(f"      🔥 MATCH ({confidence}%): {title[:50]}...")
                    self.registry.register_artifact(
                        url=url,
                        content=content,
                        source_module=self.name,
                        title=title
                    )
                else:
                    print(f"      🗑️  Trash Alert: {title[:50]}...")
                    continue

        except Exception as e:
            print(f"   ⚠️ Feed Error: {e}")

    def _extract_content(self, url):
        """Fetches and extracts clean text from a URL."""
        try:
            # Increased timeout for reliability
            page = requests.get(url, headers=self.headers, timeout=30)
            content = trafilatura.extract(page.text, include_comments=False, include_tables=False)
            
            if content and len(content) > 100:
                return content
            return None
        except Exception as e:
            print(f"      ❌ Extraction Error: {e}")
            return None