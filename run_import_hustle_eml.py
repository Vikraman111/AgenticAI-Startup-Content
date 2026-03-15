#!/usr/bin/env python3
"""
HUSTLE EML IMPORTER: One-time bulk import
Extracts articles from 50 .eml files stored in data/gmail/hustleEmails/
"""

import os
import sys
import email
import trafilatura
import requests
from bs4 import BeautifulSoup
from core.registry import Registry
from core.filter_logic import SmartFilter

def parse_eml_file(eml_path):
    """Parse .eml file and extract email data."""
    try:
        with open(eml_path, 'r', encoding='utf-8', errors='ignore') as f:
            msg = email.message_from_file(f)
        
        subject = msg.get('Subject', 'No Subject')
        sender = msg.get('From', 'Unknown')
        date = msg.get('Date', None)
        
        # Extract body
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    payload = part.get_payload(decode=True)
                    if payload:
                        body += payload.decode('utf-8', errors='ignore')
                elif part.get_content_type() == 'text/html':
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html, 'html.parser')
                        body += soup.get_text()
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')
        
        # Extract URLs
        url_pattern = r'https?://[^\s\)"\']+'
        import re
        urls = re.findall(url_pattern, body)
        
        return {
            'subject': subject,
            'from': sender,
            'date': date,
            'body': body,
            'urls': urls
        }
    except Exception as e:
        print(f"   ❌ Error parsing {eml_path}: {e}")
        return None

def extract_articles_from_email(email_data):
    """Extract articles from email URLs."""
    articles = []
    urls = email_data['urls']
    
    if not urls:
        return articles
    
    headers = {'User-Agent': 'Mozilla/5.0...'}
    
    for url in urls:
        # Skip tracking/marketing URLs
        if any(skip in url.lower() for skip in ['unsubscribe', 'profile', 'store.thehustle', '_hsenc', '_hsmi']):
            continue
        
        try:
            print(f"      🔗 Fetching: {url[:50]}...", end=" ")
            
            page = requests.get(url, headers=headers, timeout=10)
            if page.status_code != 200:
                print("❌ Failed")
                continue
            
            content = trafilatura.extract(page.text, include_comments=False, include_tables=False)
            
            if content and len(content) > 300:
                soup = BeautifulSoup(page.text, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "Hustle Article"
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

def run_eml_import():
    """Main EML import flow."""
    print("\n" + "="*80)
    print("📧 HUSTLE EML ARCHIEVE IMPORTER")
    print("="*80 + "\n")
    
    eml_dir = 'data/gmail/hustleEmails'
    
    if not os.path.exists(eml_dir):
        print(f"❌ Directory not found: {eml_dir}")
        return False
    
    # Get all .eml files
    eml_files = [f for f in os.listdir(eml_dir) if f.endswith('.eml')]
    
    if not eml_files:
        print(f"❌ No .eml files found in {eml_dir}")
        return False
    
    print(f"📧 Found {len(eml_files)} .eml files\n")
    
    # Initialize
    registry = Registry()
    filter_logic = SmartFilter()
    
    total_articles = 0
    registered_articles = 0
    
    print("📰 EXTRACTING ARTICLES FROM EML FILES\n")
    
    for i, eml_file in enumerate(eml_files, 1):
        eml_path = os.path.join(eml_dir, eml_file)
        print(f"EML {i}/{len(eml_files)}: {eml_file}")
        
        # Parse EML
        email_data = parse_eml_file(eml_path)
        if not email_data:
            continue
        
        print(f"   Subject: {email_data['subject'][:50]}")
        
        # Extract articles
        articles = extract_articles_from_email(email_data)
        
        if not articles:
            print("   No valid articles extracted.\n")
            continue
        
        print(f"   ✅ Extracted {len(articles)} articles")
        
        # Register articles
        for article in articles:
            # Quick relevance check
            is_relevant, _ = filter_logic.is_relevant(article['title'], article['content'][:200])
            
            if not is_relevant:
                print(f"      🗑️ Filtered: {article['title'][:40]}")
                continue
            
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
    print(f"\n✅ EML IMPORT COMPLETE")
    print(f"   Total articles found: {total_articles}")
    print(f"   Articles registered: {registered_articles}")
    print(f"\nNext steps:")
    print("   1. python3 run_understanding.py")
    print("   2. python3 run_scoring.py")
    print("   3. python3 tools/review_dashboard.py\n")
    
    return True

if __name__ == "__main__":
    success = run_eml_import()
    sys.exit(0 if success else 1)
