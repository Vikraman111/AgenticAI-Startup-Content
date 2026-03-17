#!/usr/bin/env python3
"""
🔥 Firebase Publishing CLI
Syncs WRITTEN posts from local SQLite DB to Firebase Firestore,
and provides tools to manage the publishing queue.

Usage:
    python run_firebase_sync.py                     # Sync all WRITTEN posts to Firebase
    python run_firebase_sync.py --limit 5           # Sync top 5 posts
    python run_firebase_sync.py --force              # Re-sync even if already in Firebase
    python run_firebase_sync.py --list               # List all posts in Firebase
    python run_firebase_sync.py --list --status NOT_POSTED  # Filter by status
    python run_firebase_sync.py --next               # Show the next post to publish
"""

import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from firebase_publishing.firebase_store import (
    sync_posts_to_firebase,
    display_firebase_posts,
    get_next_post_to_publish,
    update_post_status,
)


def main():
    parser = argparse.ArgumentParser(
        description="🔥 Firebase Publishing Queue Manager"
    )

    # Actions
    parser.add_argument(
        "--list", action="store_true",
        help="List posts stored in Firebase"
    )
    parser.add_argument(
        "--next", action="store_true",
        help="Show the next highest-scored NOT_POSTED article"
    )
    parser.add_argument(
        "--mark-posted", type=str, metavar="ARTICLE_ID",
        help="Mark a specific article as POSTED"
    )
    parser.add_argument(
        "--mark-queued", type=str, metavar="ARTICLE_ID",
        help="Mark a specific article as QUEUED"
    )

    # Options
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Number of posts to sync or list (default: all)"
    )
    parser.add_argument(
        "--status", type=str, choices=["NOT_POSTED", "QUEUED", "POSTED"],
        help="Filter posts by status (used with --list)"
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Force re-sync posts that already exist in Firebase"
    )

    args = parser.parse_args()

    print("\n🔥 Firebase Publishing Queue Manager")
    print("=" * 50 + "\n")

    # --- Action: List posts in Firebase ---
    if args.list:
        display_firebase_posts(
            status_filter=args.status,
            limit=args.limit or 10
        )
        return

    # --- Action: Get next post to publish ---
    if args.next:
        post = get_next_post_to_publish()
        if post:
            print(f"\n📝 Full post content:\n")
            print("-" * 80)
            print(post.get("final_post", "No content"))
            print("-" * 80)
        return

    # --- Action: Mark post as POSTED ---
    if args.mark_posted:
        update_post_status(args.mark_posted, "POSTED")
        return

    # --- Action: Mark post as QUEUED ---
    if args.mark_queued:
        update_post_status(args.mark_queued, "QUEUED")
        return

    # --- Default Action: Sync posts to Firebase ---
    sync_posts_to_firebase(limit=args.limit, force=args.force)


if __name__ == "__main__":
    main()
