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

def process_posts(status_filter, target_sheet_name, terminal_status):
    """General function to move posts from Firebase to a specific Google Sheet."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔍 Checking for {status_filter} posts in Firebase...")
    
    posts = list_firebase_posts(status_filter=status_filter, limit=50)
    
    if not posts:
        print(f"📭 No {status_filter} posts found.")
        return

    print(f"🚀 Found {len(posts)} posts to process for {target_sheet_name}!")
    
    client = get_sheets_client()
    if not client:
        return

    try:
        spreadsheet = client.open_by_key(SHEET_ID)
        
        # Open or create the target worksheet
        try:
            sheet = spreadsheet.worksheet(target_sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            print(f"📁 Creating new worksheet: {target_sheet_name}")
            sheet = spreadsheet.add_worksheet(title=target_sheet_name, rows="100", cols="20")
        
        # Check if header exists
        if not sheet.get_all_values():
            sheet.append_row(["Date Logged", "Score", "Title", "URL", "Content"])

        for post in posts:
            article_id = post.get("article_id")
            title = post.get("title", "")
            score = post.get("score", 0)
            url = post.get("url", "")
            content = post.get("final_post", "")
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

            print(f"📝 Logging to {target_sheet_name}: {title[:50]}...")
            
            # Append to sheet
            sheet.append_row([date_str, score, title, url, content])
            
            # Mark terminal status in Firebase
            update_post_status(article_id, terminal_status)
            print(f"✅ Successfully processed and marked as {terminal_status}.")
            
    except Exception as e:
        print(f"❌ Error during processing {status_filter}: {str(e)}")

def run_publisher_cycle():
    """Runs one full cycle of publishing Approved and archiving Rejected posts."""
    # 1. Process QUEUED -> Sheet1 (POSTED)
    process_posts(status_filter="QUEUED", target_sheet_name="Sheet1", terminal_status="POSTED")
    
    # 2. Process REJECTED -> Sheet2 (REJECTED_ARCHIVED)
    process_posts(status_filter="REJECTED", target_sheet_name="Sheet2", terminal_status="REJECTED_ARCHIVED")

if __name__ == "__main__":
    print("🛰️ Google Sheets Publisher is starting...")
    print(f"📊 Target Sheet ID: {SHEET_ID}")
    
    # Run once immediately
    run_publisher_cycle()
    
    # Then loop every 60 seconds
    print("\n⏳ Entering background loop (checking every 60s)... Press Ctrl+C to stop.")
    while True:
        try:
            time.sleep(60)
            run_publisher_cycle()
        except KeyboardInterrupt:
            print("\n👋 Stopping Publisher.")
            break
        except Exception as e:
            print(f"⚠️ Loop error: {e}")
            time.sleep(10)
