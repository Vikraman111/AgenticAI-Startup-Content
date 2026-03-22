#!/usr/bin/env python3
"""
STAGE 1: Content Extraction & Monitoring
Fetches articles from RSS feeds and stores them in the database.
"""

from monitoring.techcrunch_crawler import TechCrunchCrawler
from monitoring.crunchbase_crawler import CrunchbaseCrawler
from monitoring.venturebeat_crawler import VentureBeatCrawler
from monitoring.fastcompany_crawler import FastCompanyCrawler
from monitoring.afterschool_crawler import AfterschoolCrawler
from monitoring.business_insider_crawler import BusinessInsiderCrawler
from monitoring.hustle_crawler import HustleCrawler
from monitoring.forbes_crawler import ForbesCrawler
from monitoring.hbr_crawler import HBRCrawler
from monitoring.entrepreneur_crawler import EntrepreneurCrawler
from monitoring.inc_crawler import IncCrawler

def run_monitoring():
    print("\n" + "="*80)
    print("📡 MONITORING STAGE: Content Extraction from RSS Feeds")
    print("="*80 + "\n")
    
    from core.registry import Registry
    reg = Registry()
    
    # 🧪 Check for Deep Scan (Empty DB)
    cursor = reg.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM artifacts")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("🚀 FIRST RUN DETECTED: Starting Deep Historical Scan (30 Days)...")
        from monitoring.deep_sitemap_crawler import DeepSitemapCrawler
        deep_crawler = DeepSitemapCrawler()
        deep_crawler.run()
        print("\n✅ Deep Historical Scan Complete. Proceeding with Live Feeds...")

    crawlers = [
        TechCrunchCrawler(),
        CrunchbaseCrawler(),
        VentureBeatCrawler(),
        FastCompanyCrawler(),
        AfterschoolCrawler(),
        BusinessInsiderCrawler(),
        HustleCrawler(),
        ForbesCrawler(),
        HBRCrawler(),
        EntrepreneurCrawler(),
        IncCrawler(),
    ]
    
    for crawler in crawlers:
        crawler.run()
    
    print("\n✅ Monitoring complete. Articles stored in database.")

if __name__ == "__main__":
    run_monitoring()
