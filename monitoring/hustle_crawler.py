import sys
import trafilatura
import requests
from bs4 import BeautifulSoup
from monitoring.gmail_client import GmailClient
from core.registry import Registry
from core.filter_logic import SmartFilter

class HustleCrawler:
    def __init__(self):
        self.source_name = "Hustle_Email"
        self.gmail_client = GmailClient()
        self.registry = Registry()
        self.filter_logic = SmartFilter()
        
    def extract_articles_from_email(self, email_data):
        """
        Extract article URLs from email and fetch their full content.
        Returns list of article dicts.
        """
        articles = []
        urls = email_data.get('urls', [])
        
        if not urls:
            return articles
        
        print(f"   Extracting {len(urls)} URLs from email: {email_data.get('subject', 'No Subject')[:40]}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        
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
                        'source': self.source_name
                    }
                    articles.append(article)
                    print(f"✅ ({len(content)} chars)")
                else:
                    print("⚠️ Content too short")
            
            except Exception as e:
                print(f"❌ {str(e)[:30]}")
        
        return articles

    def run(self):
        print(f"\n[{self.source_name}] Fetching unread emails...")
        emails = self.gmail_client.fetch_emails(sender_email='news@thehustle.co', max_results=10, unread_only=True)
        
        if not emails:
            print("❌ No new emails found!")
            return
        
        print(f"✅ Found {len(emails)} emails\n")
        
        total_articles = 0
        registered_articles = 0
        
        for i, email in enumerate(emails, 1):
            print(f"Email {i}/{len(emails)}: {email.get('subject', 'No Subject')}")
            articles = self.extract_articles_from_email(email)
            
            if not articles:
                print("   No valid articles extracted.\n")
                continue
            
            print(f"   ✅ Extracted {len(articles)} articles")
            
            # Register articles
            for article in articles:
                is_relevant, _ = self.filter_logic.is_relevant(article['title'], article['content'][:200])
                
                if not is_relevant:
                    print(f"      🗑️ Filtered: {article['title'][:40]}")
                    continue
                
                success = self.registry.register_artifact(
                    url=article['url'],
                    content=article['content'],
                    source_module=self.source_name,
                    title=article['title']
                )
                
                if success:
                    registered_articles += 1
                    print(f"      ✅ Registered: {article['title'][:40]}")
                else:
                    print(f"      ⏭️ Duplicate: {article['title'][:40]}")
            
            total_articles += len(articles)
            
            # Mark the email as read so we don't process it again
            self.gmail_client.mark_as_read(email['message_id'])
            print("   📨 Marked email as read.")
            print()
            
        print(f"[{self.source_name}] Complete: {registered_articles} registered from {total_articles} extracted.")
