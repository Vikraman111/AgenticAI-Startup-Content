import os
import sys
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import list_firebase_posts, update_post_status

# Load environment variables
load_dotenv()

# Google Sheets Config
SHEET_ID = os.environ.get("GOOGLE_SHEET_ID")
CREDS_FILE = "google_sheets_credentials.json"

def get_sheets_client():
    """Initializes the Google Sheets client using the service account credentials."""
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), CREDS_FILE)
    
    if not os.path.exists(creds_path):
        print(f"❌ Error: {CREDS_FILE} not found at {creds_path}")
        return None

    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
        client = gspread.authorize(creds)
        return client
    except Exception as e:
        print(f"❌ Error authenticating with Google Sheets: {e}")
        return None

def publish_queued_posts():
    """Checks Firebase for QUEUED posts and appends them to the Google Sheet."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking for QUEUED posts in Firebase...")
    
    queued_posts = list_firebase_posts(status_filter="QUEUED", limit=50)
    
    if not queued_posts:
        print("📭 No QUEUED posts found.")
        return

    print(f"🚀 Found {len(queued_posts)} posts to publish!")
    
    client = get_sheets_client()
    if not client:
        return

    try:
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Check if header exists, if not, create it
        if not sheet.get_all_values():
            sheet.append_row(["Date Published", "Score", "Title", "URL", "LinkedIn Post Body"])

        for post in queued_posts:
            article_id = post.get("article_id")
            title = post.get("title", "")
            score = post.get("score", 0)
            url = post.get("url", "")
            final_post = post.get("final_post", "")
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            print(f"📝 Appending row: {title[:50]}...")
            
            # Append to sheet
            sheet.append_row([date_str, score, title, url, final_post])
            
            # Mark as POSTED in Firebase
            update_post_status(article_id, "POSTED")
            print(f"✅ Successfully published and marked as POSTED.")
            
    except Exception as e:
        print(f"❌ Error during publishing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🛰️ Google Sheets Publisher is starting...")
    print(f"📊 Target Sheet ID: {SHEET_ID}")
    
    # Run once immediately
    publish_queued_posts()
    
    # Then loop every 60 seconds
    print("\n⏳ Entering background loop (checking every 60s)... Press Ctrl+C to stop.")
    while True:
        try:
            time.sleep(60)
            publish_queued_posts()
        except KeyboardInterrupt:
            print("\n👋 Stopping Publisher.")
            break
        except Exception as e:
            print(f"⚠️ Loop error: {e}")
            time.sleep(10)
