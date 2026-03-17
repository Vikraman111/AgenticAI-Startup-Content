import os
import sys
import sqlite3
import shutil

# Add project root to path so we can import from firebase_publishing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_config import get_firestore_client, POSTS_COLLECTION

def nuke_local_db():
    """Deletes the agent_registry.db and artifacts.db files."""
    db_paths = ["data/agent_registry.db", "artifacts.db"]
    
    print("\n--- 🗑️ Resetting Local Databases ---")
    for path in db_paths:
        abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
                print(f"✅ Deleted: {path}")
            except Exception as e:
                print(f"❌ Error deleting {path}: {e}")
        else:
            print(f"⏭️ Not found (already clean): {path}")

def nuke_firebase_collection():
    """Deletes all documents in the linkedin_posts collection in Firestore."""
    print("\n--- 🔥 Resetting Firebase (Firestore) ---")
    
    try:
        db = get_firestore_client()
        collection_ref = db.collection(POSTS_COLLECTION)
        
        # Firestore batch delete for all documents in the collection
        docs = list(collection_ref.stream())
        if not docs:
            print(f"⏭️ Firebase collection '{POSTS_COLLECTION}' is already empty.")
            return

        print(f"⚠️ Found {len(docs)} documents in '{POSTS_COLLECTION}'. Deleting...")
        
        # Batching for safety/performance
        batch = db.batch()
        count = 0
        for doc in docs:
            batch.delete(doc.reference)
            count += 1
            if count % 500 == 0:
                batch.commit()
                batch = db.batch()

        batch.commit()
        print(f"✅ Successfully purged all {len(docs)} documents from Firestore.")
        
    except Exception as e:
        print(f"❌ Error resetting Firebase: {e}")

if __name__ == "__main__":
    print("🚨 WARNING: This will permanently DELETE your entire local history")
    print("   and PURGE all unposted articles from Firebase Firestore.")
    
    confirm = input("\nAre you absolutely sure you want to proced? (yes/no): ").strip().lower()
    
    if confirm == "yes":
        print("\n🚀 Initiating Total System Reset...")
        nuke_local_db()
        nuke_firebase_collection()
        print("\n✨ Clean slate achieved! You can now run your pipeline from step 1.")
    else:
        print("\n❌ Reset aborted.")
