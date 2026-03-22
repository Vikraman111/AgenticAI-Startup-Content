#!/usr/bin/env python3
import sqlite3
import sys

def reset_pipeline():
    """Reset articles to 'DISCOVERED' status if they haven't been published."""
    try:
        conn = sqlite3.connect('data/agent_registry.db')
        cursor = conn.cursor()
        
        # We target items that are in various stages but NOT yet 'POSTED' or 'FIREBASE_SYNCED'
        # This allows the new improved agents to re-process and re-score them.
        cursor.execute("""
            UPDATE artifacts 
            SET status = 'DISCOVERED', 
                score = 0, 
                summary = NULL, 
                strategic_insight = NULL, 
                relevance_reasoning = NULL 
            WHERE status NOT IN ('POSTED', 'FIREBASE_SYNCED')
        """)
        
        count = conn.total_changes
        conn.commit()
        conn.close()
        
        print(f"🔄 SUCCESS: Reset {count} articles back to 'DISCOVERED' status.")
        print("   They will now be re-processed using the improved OpenAI-powered agents.")
        
    except Exception as e:
        print(f"⚠️ Error resetting pipeline: {e}")

if __name__ == "__main__":
    confirm = input("This will reset all non-published articles for re-processing. Continue? (y/n): ")
    if confirm.lower() == 'y':
        reset_pipeline()
    else:
        print("Aborted.")
