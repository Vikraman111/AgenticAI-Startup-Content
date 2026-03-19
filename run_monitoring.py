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
