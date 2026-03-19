import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from firebase_publishing.firebase_store import list_firebase_posts

def check_firebase():
    load_dotenv()
    for status in ["NOT_POSTED", "QUEUED", "POSTED", "REJECTED"]:
        posts = list_firebase_posts(status_filter=status, limit=100)
        print(f"Status: {status} | Count: {len(posts)}")
        for p in posts:
            print(f"  - [{p['article_id'][:8]}] {p['title'][:50]}")

if __name__ == "__main__":
    check_firebase()
