#!/usr/bin/env python3
import sqlite3
import sys
import os

# Add project root to path for Firebase imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_config import get_firestore_client, POSTS_COLLECTION

def full_reset():
    """Wipes all data from local SQLite and Firebase Firestore for a fresh start."""
    print("\n" + "!"*50)
    print("🔥 NUCLEAR RESET: Wiping all article data")
    print("!"*50 + "\n")
    
    # 1. WIPE LOCAL SQLITE
    try:
        db_path = 'data/agent_registry.db'
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Delete all rows from artifacts
            cursor.execute("DELETE FROM artifacts")
            count = conn.total_changes
            conn.commit()
            conn.close()
            print(f"✅ Local DB: Deleted {count} artifacts.")
        else:
            print("⚠️ Local DB: data/agent_registry.db not found.")
    except Exception as e:
        print(f"❌ Local DB Error: {e}")

    # 2. WIPE FIREBASE FIRESTORE
    try:
        db = get_firestore_client()
        collection_ref = db.collection(POSTS_COLLECTION)
        
        # Batch delete documents (Firestore doesn't have a simple 'delete all')
        docs = collection_ref.stream()
        deleted_count = 0
        
        batch = db.batch()
        for doc in docs:
            batch.delete(doc.reference)
            deleted_count += 1
            # Commit batches in groups of 500 (Firestore limit)
            if deleted_count % 500 == 0:
                batch.commit()
                batch = db.batch()
        
        batch.commit()
        print(f"✅ Firebase: Deleted {deleted_count} documents from '{POSTS_COLLECTION}'.")
    except Exception as e:
        print(f"❌ Firebase Error: {e}")

    print("\n✨ ALL DATA WIPED. The next run will be a completely fresh scan.\n")

if __name__ == "__main__":
    confirm = input("⚠️  WARNING: This will permanently DELETE all articles from Local DB and Firebase. Proceed? (y/n): ")
    if confirm.lower() == 'y':
        full_reset()
    else:
        print("Aborted.")
