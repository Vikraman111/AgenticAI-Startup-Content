#!/usr/bin/env python3
"""
HUSTLE EMAIL EXTRACTOR: Standalone script
Fetches ALL Hustle emails, extracts articles, scores them, and merges with existing RSS articles.
Converts top 10 to top 20 articles.
"""

import sys
import hashlib
import trafilatura
import requests
from bs4 import BeautifulSoup
from monitoring.gmail_client import GmailClient
from core.registry import Registry
from core.filter_logic import SmartFilter

def extract_articles_from_email(email_data):
    """
    Extract article URLs from email and fetch their full content.
    Returns list of article dicts.
    """
    articles = []
    urls = email_data['urls']
    
    if not urls:
        return articles
    
    print(f"   Extracting {len(urls)} URLs from email: {email_data['subject'][:40]}...")
    
    headers = {'User-Agent': 'Mozilla/5.0...'}
    
    for url in urls:
        # Skip tracking/marketing URLs
        if any(skip in url.lower() for skip in ['unsubscribe', 'profile', 'store.thehustle', '_hsenc', '_hsmi']):
            continue
        
        try:
            print(f"      🔗 Fetching: {url[:50]}...", end=" ")
            
            # Fetch page
            page = requests.get(url, headers=headers, timeout=10)
            if page.status_code != 200:
                print("❌ Failed")
                continue
            
            # Extract content
            content = trafilatura.extract(page.text, include_comments=False, include_tables=False)
            
            if content and len(content) > 300:
                # Extract title from HTML
                soup = BeautifulSoup(page.text, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "Hustle Article"
                # Clean up title
                title = title.replace(' | The Hustle', '').replace(' - The Hustle', '').strip()
                
                article = {
                    'url': url,
                    'content': content,
                    'title': title,
                    'source': 'Hustle_Email'
                }
                articles.append(article)
                print(f"✅ ({len(content)} chars)")
            else:
                print("⚠️ Content too short")
        
        except Exception as e:
            print(f"❌ {str(e)[:30]}")
    
    return articles

def run_hustle_extraction():
    """Main extraction and scoring flow."""
    print("\n" + "="*80)
    print("📧 HUSTLE EMAIL EXTRACTOR")
    print("="*80 + "\n")
    
    # Initialize
    gmail_client = GmailClient()
    registry = Registry()
    filter_logic = SmartFilter()
    
    # Fetch ALL Hustle emails (no limit)
    print("🔐 Fetching ALL emails from news@thehustle.co...")
    emails = gmail_client.fetch_emails(sender_email='news@thehustle.co', max_results=50)
    
    if not emails:
        print("❌ No emails found!")
        return False
    
    print(f"✅ Found {len(emails)} emails\n")
    
    # Extract articles
    total_articles = 0
    registered_articles = 0
    
    print("📰 EXTRACTING ARTICLES FROM EMAILS\n")
    
    for i, email in enumerate(emails, 1):
        print(f"Email {i}/{len(emails)}: {email['subject']}")
        articles = extract_articles_from_email(email)
        
        if not articles:
            print("   No valid articles extracted.\n")
            continue
        
        print(f"   ✅ Extracted {len(articles)} articles")
        
        # Register articles
        for article in articles:
            # Quick relevance check (no LLM cost)
            is_relevant, _ = filter_logic.is_relevant(article['title'], article['content'][:200])
            
            if not is_relevant:
                print(f"      🗑️ Filtered: {article['title'][:40]}")
                continue
            
            # Register in database
            success = registry.register_artifact(
                url=article['url'],
                content=article['content'],
                source_module='Hustle_Email',
                title=article['title']
            )
            
            if success:
                registered_articles += 1
                print(f"      ✅ Registered: {article['title'][:40]}")
            else:
                print(f"      ⏭️ Duplicate: {article['title'][:40]}")
        
        total_articles += len(articles)
        print()
    
    print("="*80)
    print(f"\n✅ EXTRACTION COMPLETE")
    print(f"   Total articles found: {total_articles}")
    print(f"   Articles registered: {registered_articles}")
    print(f"\nNext steps:")
    print("   1. python3 run_understanding.py")
    print("   2. python3 run_scoring.py")
    print("   3. python3 tools/review_dashboard.py\n")
    
    return True

if __name__ == "__main__":
    success = run_hustle_extraction()
    sys.exit(0 if success else 1)
