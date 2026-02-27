import feedparser
import trafilatura
from core.registry import Registry

class MonitoringAgent:
    def __init__(self):
        self.registry = Registry()
        self.sources = [
            "https://news.crunchbase.com/feed/",
            "https://afterschool.substack.com/feed",
            "https://www.fastcompany.com/rss"
        ]

    def run(self):
        print("🕵️ MONITORING AGENT: Scanning sources...")
        new_count = 0
        
        for source in self.sources:
            feed = feedparser.parse(source)
            for entry in feed.entries[:3]: # Limit to latest 3
                url = entry.link
                
                # 1. Fetch Full Content (Trafilatura)
                downloaded = trafilatura.fetch_url(url)
                if downloaded:
                    text = trafilatura.extract(downloaded)
                    if text:
                        # 2. Register into System
                        is_new = self.registry.register_artifact(
                            url=url, 
                            content=text, 
                            source=source, 
                            title=entry.title
                        )
                        if is_new:
                            print(f"   found: {entry.title[:30]}...")
                            new_count += 1
        
        print(f"🕵️ MONITORING AGENT: Registered {new_count} new artifacts.")