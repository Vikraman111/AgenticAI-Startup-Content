import hashlib
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from core.registry import Registry
from core.filter_logic import SmartFilter

class DeepSitemapCrawler:
    """
    SPECIAL CRAWLER: Used only on First Run (Empty DB).
    Goes back 30 days using Sitemaps to find historical articles.
    """
    def __init__(self):
        self.registry = Registry()
        self.filter = SmartFilter()
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def _generate_id(self, url):
        """Standard SHA256 ID generation."""
        return hashlib.sha256(url.encode()).hexdigest()

    def _extract_content(self, url):
        import trafilatura
        try:
            page = requests.get(url, headers=self.headers, timeout=20)
            content = trafilatura.extract(page.text, include_comments=False)
            return content
        except:
            return None

    def capture_techcrunch(self, days=30):
        print(f"📡 [TechCrunch] Deep Scanning last {days} days...")
        url = "https://techcrunch.com/sitemap-page-1.xml"
        try:
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'xml')
            urls = soup.find_all('url')
            
            cutoff = datetime.now() - timedelta(days=days)
            matches = 0
            
            for entry in urls:
                loc_tag = entry.find('loc')
                if not loc_tag: continue
                loc = loc_tag.text
                
                # TechCrunch formatting varies: can be 2026-03-22 or 2026-03-22T12:00:00Z
                lastmod_tag = entry.find('lastmod')
                if not lastmod_tag: continue
                lastmod_str = lastmod_tag.text.split('T')[0] # Keep only date part
                
                try:
                    lastmod = datetime.strptime(lastmod_str, '%Y-%m-%d')
                except:
                    continue
                
                if lastmod > cutoff:
                    if self.registry.exists(self._generate_id(loc)): continue
                    
                    # slug check for fast-kill
                    slug = loc.split('/')[-2].replace('-', ' ') if '/' in loc else ""
                    if not slug or not slug.strip(): continue
                    
                    sim_score = self.filter.get_strategic_score(slug)
                    
                    if sim_score > 0.12: # Lowered for slug-only precision
                        content = self._extract_content(loc)
                        if content and len(content) > 500:
                            title = slug.title()
                            is_rel, conf = self.filter.is_relevant(title, content[:500])
                            if is_rel:
                                self.registry.register_artifact(loc, content, "TechCrunch_Deep", title)
                                matches += 1
                                print(f"   🔥 Deep Match: {title[:50]}...")
            
            print(f"✅ TechCrunch Deep Scan: Found {matches} articles.")
        except Exception as e:
            print(f"❌ TechCrunch Deep Error: {e}")

    def capture_crunchbase(self, days=30):
        print(f"📡 [Crunchbase] Deep Scanning last {days} days...")
        url = "https://news.crunchbase.com/post-sitemap.xml" # Common WP sitemap
        try:
            r = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(r.text, 'xml')
            urls = soup.find_all('url')
            
            cutoff = datetime.now() - timedelta(days=days)
            matches = 0
            
            for entry in urls:
                loc_tag = entry.find('loc')
                if not loc_tag: continue
                loc = loc_tag.text
                
                lastmod_tag = entry.find('lastmod')
                if not lastmod_tag: continue
                lastmod_str = lastmod_tag.text.split('T')[0]
                
                try:
                    lastmod = datetime.strptime(lastmod_str, '%Y-%m-%d')
                except: continue
                
                if lastmod > cutoff:
                    if self.registry.exists(self._generate_id(loc)): continue
                    
                    slug = loc.split('/')[-2].replace('-', ' ') if '/' in loc else ""
                    if not slug or not slug.strip(): continue
                    
                    if self.filter.get_strategic_score(slug) > 0.12:
                        content = self._extract_content(loc)
                        if content and len(content) > 500:
                            is_rel, conf = self.filter.is_relevant(slug.title(), content[:500])
                            if is_rel:
                                self.registry.register_artifact(loc, content, "Crunchbase_Deep", slug.title())
                                matches += 1
                                print(f"   🔥 Deep Match: {slug[:40]}...")
            print(f"✅ Crunchbase Deep Scan: Found {matches} articles.")
        except Exception as e:
            print(f"⚠️ Crunchbase Deep Error: {e}")

    def capture_venturebeat(self, days=30):
        print(f"📡 [VentureBeat] Skipping Deep Sitemap (Vercel Challenge Detected). Using RSS.")
        # VentureBeat is currently blocking automated daily sitemap queries with a 429 challenge.
        return

    def run(self):
        # Only run these on First Run
        self.capture_techcrunch()
        self.capture_crunchbase()
        self.capture_venturebeat()
