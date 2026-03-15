#!/usr/bin/env python3
"""
STANDALONE TEST: Gmail Monitor
Test script to validate Gmail fetching and parsing before full integration.
Run this first to ensure emails are being read correctly.
"""

import os
import sys
from monitoring.gmail_client import GmailClient

def test_gmail_connection():
    """Test Gmail connection and fetch emails."""
    print("\n" + "="*80)
    print("🧪 GMAIL MONITOR TEST")
    print("="*80 + "\n")
    
    # Check if credentials exist
    if not os.path.exists('data/gmail/credentials.json'):
        print("❌ ERROR: credentials.json not found in data/gmail/")
        print("   Please follow the setup instructions to get your credentials.json")
        return False
    
    try:
        # Initialize Gmail client
        print("🔐 Authenticating with Gmail...")
        client = GmailClient()
        
        # Fetch emails
        print("\n📧 Fetching emails from news@thehustle.co...")
        emails = client.fetch_emails(sender_email='news@thehustle.co', max_results=5)
        
        if not emails:
            print("   No emails found. Check if you have emails from this sender.")
            return False
        
        # Display results
        print(f"\n✅ Successfully fetched {len(emails)} emails!\n")
        print("="*80)
        
        for i, email in enumerate(emails, 1):
            print(f"\n📨 EMAIL #{i}")
            print("-" * 80)
            print(f"Subject: {email['subject']}")
            print(f"From: {email['from']}")
            print(f"Date: {email['date']}")
            print(f"\nURLs Found: {len(email['urls'])}")
            
            if email['urls']:
                for url in email['urls'][:3]:  # Show first 3 URLs
                    print(f"  🔗 {url}")
                if len(email['urls']) > 3:
                    print(f"  ... and {len(email['urls']) - 3} more URLs")
            
            print(f"\nBody Preview (first 300 chars):")
            print(f"{email['body'][:300]}...\n")
        
        print("="*80)
        print("\n✅ GMAIL TEST PASSED!")
        print("   Emails are being fetched and parsed correctly.")
        print("   Ready for integration with main pipeline.\n")
        return True
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("   Check that:")
        print("   1. credentials.json is in data/gmail/")
        print("   2. Gmail API is enabled in Google Cloud Console")
        print("   3. You have emails from news@thehustle.co\n")
        return False

if __name__ == "__main__":
    success = test_gmail_connection()
    sys.exit(0 if success else 1)
