"""
Firebase Post Store
Handles reading posts from the local SQLite DB and syncing them to Firestore.

Firestore Document Schema (per post):
{
    "article_id": str,          # SHA256 hash from local DB
    "title": str,               # Article title
    "url": str,                 # Original source URL
    "source_module": str,       # Where it was crawled from
    "score": int,               # Quality/relevance score
    "relevance_reasoning": str, # Why this article was scored high
    "strategic_insight": str,   # Business breakdown / insight
    "final_post": str,          # The generated LinkedIn post content
    "posting_status": str,      # "NOT_POSTED" | "QUEUED" | "POSTED"
    "published_date": str,      # Original article publish date
    "created_at": str,          # When it was first crawled
    "synced_to_firebase_at": datetime,  # When it was pushed to Firestore
    "posted_at": datetime | None,       # When it was actually posted to LinkedIn
}
"""
import sys
import os
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_config import get_firestore_client, POSTS_COLLECTION

# Path to the local SQLite database
LOCAL_DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "agent_registry.db"
)


def fetch_written_posts_from_local_db(limit=None):
    """
    Fetches all posts with status 'WRITTEN' and a non-empty final_post
    from the local SQLite database, ordered by score descending.
    """
    conn = sqlite3.connect(LOCAL_DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    query = """
        SELECT id, url, source_module, title, summary, score, 
               relevance_reasoning, strategic_insight, final_post,
               published_date, created_at
        FROM artifacts
        WHERE status = 'WRITTEN' AND final_post IS NOT NULL AND final_post != ''
        ORDER BY score DESC
    """
    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query)
    cols = [desc[0] for desc in cursor.description]
    rows = [dict(zip(cols, row)) for row in cursor.fetchall()]
    conn.close()
    return rows


def mark_local_post_synced(article_id):
    """Updates local SQLite status to 'FIREBASE_SYNCED' to avoid re-fetching."""
    conn = sqlite3.connect(LOCAL_DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("UPDATE artifacts SET status = 'FIREBASE_SYNCED' WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()


def sync_posts_to_firebase(limit=None, force=False):
    """
    Reads WRITTEN posts from local SQLite DB and pushes them to Firestore.

    Args:
        limit: Max number of posts to sync (None = all)
        force: If True, re-sync even if the post already exists in Firestore

    Returns:
        dict with counts: {"synced": int, "skipped": int, "errors": int}
    """
    db = get_firestore_client()
    collection_ref = db.collection(POSTS_COLLECTION)

    posts = fetch_written_posts_from_local_db(limit=limit)

    if not posts:
        print("📭 No WRITTEN posts found in local database.")
        return {"synced": 0, "skipped": 0, "errors": 0}

    print(f"\n🔄 Found {len(posts)} WRITTEN posts in local DB. Syncing to Firebase...\n")

    stats = {"synced": 0, "skipped": 0, "errors": 0}

    for post in posts:
        article_id = post["id"]

        try:
            # Check if already exists in Firestore (skip duplicates)
            if not force:
                existing_doc = collection_ref.document(article_id).get()
                if existing_doc.exists:
                    print(f"   ⏭️  Already in Firebase: {post['title'][:60]}...")
                    stats["skipped"] += 1
                    
                    # Update local DB so it doesn't get fetched next time
                    mark_local_post_synced(article_id)
                    continue

            # Build the Firestore document
            firestore_doc = {
                "article_id": article_id,
                "title": post.get("title", "Untitled"),
                "url": post.get("url", ""),
                "source_module": post.get("source_module", ""),
                "score": post.get("score", 0),
                "relevance_reasoning": post.get("relevance_reasoning", ""),
                "strategic_insight": post.get("strategic_insight", ""),
                "final_post": post.get("final_post", ""),
                "posting_status": "NOT_POSTED",
                "published_date": post.get("published_date"),
                "created_at": post.get("created_at"),
                "synced_to_firebase_at": datetime.utcnow(),
                "posted_at": None,
            }

            # Use article_id as the document ID for easy lookups
            collection_ref.document(article_id).set(firestore_doc)
            print(f"   ✅ Synced: {post['title'][:60]}... (Score: {post.get('score', 'N/A')})")
            stats["synced"] += 1
            
            # Update local DB so it doesn't get fetched next time
            mark_local_post_synced(article_id)

        except Exception as e:
            print(f"   ❌ Error syncing '{post.get('title', 'Unknown')}': {e}")
            stats["errors"] += 1

    print(f"\n📊 Sync Summary: {stats['synced']} synced | {stats['skipped']} skipped | {stats['errors']} errors")
    return stats


def list_firebase_posts(status_filter=None, limit=10):
    """
    Lists posts stored in Firebase Firestore, sorting by score entirely locally 
    to prevent Firebase Composite Index requirement errors.
    """
    from google.cloud.firestore_v1.base_query import FieldFilter

    db = get_firestore_client()
    collection_ref = db.collection(POSTS_COLLECTION)
    
    if status_filter:
        query = collection_ref.where(filter=FieldFilter("posting_status", "==", status_filter))
    else:
        query = collection_ref

    docs = list(query.stream())
    posts = [doc.to_dict() for doc in docs]
    
    # Sort locally in Python
    posts.sort(key=lambda x: x.get("score", 0), reverse=True)

    return posts[:limit]


def display_firebase_posts(status_filter=None, limit=10):
    """
    Pretty-prints posts from Firebase.
    """
    db = get_firestore_client()
    collection_ref = db.collection(POSTS_COLLECTION)

    from google.cloud.firestore_v1.base_query import FieldFilter
    # Build query
    if status_filter:
        query = collection_ref.where(filter=FieldFilter("posting_status", "==", status_filter)).limit(limit)
    else:
        query = collection_ref.limit(limit)

    docs = query.stream()
    posts = [doc.to_dict() for doc in docs]

    if not posts:
        status_msg = f" with status '{status_filter}'" if status_filter else ""
        print(f"\n📭 No posts found in Firebase{status_msg}.")
        return

    filter_label = f"(Filter: {status_filter})" if status_filter else "(All)"
    print(f"\n{'=' * 80}")
    print(f"🔥 FIREBASE POSTS {filter_label} — {len(posts)} posts")
    print(f"{'=' * 80}\n")

    for idx, post in enumerate(posts, 1):
        status_emoji = {
            "NOT_POSTED": "⏳",
            "QUEUED": "📋",
            "POSTED": "✅"
        }.get(post.get("posting_status", ""), "❓")

        print(f"POST #{idx} | Score: {post.get('score', 'N/A')} | Status: {status_emoji} {post.get('posting_status', 'UNKNOWN')}")
        print(f"TITLE: {post.get('title', 'Untitled')}")
        print(f"🔗 LINK: {post.get('url', 'N/A')}")
        print(f"-" * 80)
        content = post.get("final_post", "No content")
        print(content[:300] + "..." if len(content) > 300 else content)
        print(f"\n{'=' * 80}\n")


def update_post_status(article_id, new_status):
    """
    Updates the posting_status of a specific post in Firestore.

    Args:
        article_id: The document ID (article hash)
        new_status: New status string ("NOT_POSTED", "QUEUED", "POSTED", "REJECTED")
    """
    valid_statuses = ["NOT_POSTED", "QUEUED", "POSTED", "REJECTED"]
    if new_status not in valid_statuses:
        print(f"❌ Invalid status '{new_status}'. Must be one of: {valid_statuses}")
        return False

    db = get_firestore_client()
    doc_ref = db.collection(POSTS_COLLECTION).document(article_id)

    doc = doc_ref.get()
    if not doc.exists:
        print(f"❌ Post with ID '{article_id}' not found in Firebase.")
        return False

    update_data = {"posting_status": new_status}
    if new_status == "POSTED":
        update_data["posted_at"] = datetime.utcnow()

    doc_ref.update(update_data)
    print(f"✅ Updated post '{article_id[:16]}...' status to: {new_status}")
    return True


def get_next_post_to_publish():
    """
    Gets the highest-scored NOT_POSTED article from Firebase.
    Sorted locally in Python to bypass Firebase Composite Index errors.
    """
    from google.cloud.firestore_v1.base_query import FieldFilter
    db = get_firestore_client()
    collection_ref = db.collection(POSTS_COLLECTION)

    query = collection_ref.where(filter=FieldFilter("posting_status", "==", "NOT_POSTED"))
    
    docs = list(query.stream())
    if not docs:
        print("📭 No NOT_POSTED articles available.")
        return None

    posts = [doc.to_dict() for doc in docs]
    # Sort in Python by score descending
    posts.sort(key=lambda x: x.get("score", 0), reverse=True)
    
    post = posts[0]
    print(f"📌 Next post to publish: {post.get('title', 'Untitled')} (Score: {post.get('score', 'N/A')})")
    return post
