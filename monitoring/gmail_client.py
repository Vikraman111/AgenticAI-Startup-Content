import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
# from google.api_python_client import discovery
from googleapiclient import discovery
from bs4 import BeautifulSoup
import re
from email.mime.text import MIMEText

# Required scopes for reading and marking as read
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
CREDENTIALS_PATH = 'data/gmail/credentials.json'
TOKEN_PATH = 'data/gmail/token.pickle'

class GmailClient:
    def __init__(self):
        self.service = None
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with Gmail API. Opens browser on first run."""
        creds = None
        
        # Load existing token if available
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token_file:
                creds = pickle.load(token_file)
        
        # If no valid token, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # First time - opens browser for consent
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for future use
            with open(TOKEN_PATH, 'wb') as token_file:
                pickle.dump(creds, token_file)
        
        self.service = discovery.build('gmail', 'v1', credentials=creds)
        print("✅ Gmail authenticated successfully!")
    
    def fetch_emails(self, sender_email='news@thehustle.co', max_results=10, unread_only=False, newer_than=None):
        """
        Fetch emails with advanced filtering.
        
        Args:
            sender_email: Email address to fetch from
            max_results: Maximum number of emails to fetch
            unread_only: Whether to fetch only unread emails
            newer_than: Gmail interval like '30d', '1y' etc.
        """
        try:
            # Search for emails from sender
            query = f"from:{sender_email}"
            if unread_only:
                query += " is:unread"
            if newer_than:
                query += f" newer_than:{newer_than}"
                
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print(f"   No emails found from {sender_email}")
                return []
            
            print(f"   📧 Found {len(messages)} emails from {sender_email}")
            
            emails = []
            for msg in messages:
                try:
                    email_data = self._parse_message(msg['id'])
                    if email_data:
                        emails.append(email_data)
                except Exception as e:
                    print(f"      ⚠️  Error parsing email: {e}")
            
            return emails
        
        except Exception as e:
            print(f"   ❌ Gmail API Error: {e}")
            return []
    
    def _parse_message(self, message_id):
        """Extract content from email message."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), None)
            
            # Extract body
            body = self._get_message_body(message['payload'])
            
            if not body:
                return None
            
            # Extract URLs from email
            urls = self._extract_urls(body)
            
            email_obj = {
                'message_id': message_id,
                'subject': subject,
                'from': sender,
                'date': date,
                'body': body,
                'urls': urls
            }
            
            return email_obj
        
        except Exception as e:
            print(f"      Error parsing message {message_id}: {e}")
            return None
    
    def _get_message_body(self, payload):
        """Extract text body from email payload."""
        try:
            # Check if body exists in parts
            if 'parts' in payload:
                body = ''
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        if data:
                            body += base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        data = part['body'].get('data', '')
                        if data:
                            html = base64.urlsafe_b64decode(data).decode('utf-8')
                            # Convert HTML to plain text
                            soup = BeautifulSoup(html, 'html.parser')
                            body += soup.get_text()
                return body if body else None
            else:
                # Single part message
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            print(f"      Error extracting body: {e}")
        
        return None
    
    def _extract_urls(self, text):
        """Extract URLs from text."""
        url_pattern = r'https?://[^\s\)"\']+'
        return re.findall(url_pattern, text)

    def mark_as_read(self, message_id):
        """Mark an email as read by removing the UNREAD label."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        except Exception as e:
            print(f"      ⚠️  Error marking message {message_id} as read: {e}")
