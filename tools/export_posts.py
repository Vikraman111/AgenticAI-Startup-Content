import sys
import os
import sqlite3

# --- PATH FIX: Allow importing from parent directory ---
# This adds the project root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# -------------------------------------------------------

DB_PATH = "data/agent_registry.db"

def export_posts():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        cursor = conn.cursor()
        
        # Only fetch items that have a final_post generated
        cursor.execute("SELECT title, score, url, final_post FROM artifacts WHERE final_post IS NOT NULL AND final_post != '' ORDER BY score DESC")
        
        items = cursor.fetchall()
        
        if not items:
            print("\n📭 No final posts have been generated yet.")
            print("   (Run python3 run_writer.py first)")
            return

        print("\n" + "="*80)
        print(f"📝 GENERATED POSTS ({len(items)} Ready)")
        print("="*80 + "\n")
        
        for idx, (title, score, url, content) in enumerate(items, 1):
            print(f"POST #{idx} | Source Score: {score}")
            print(f"TITLE: {title}")
            print(f"🔗 LINK: {url}")
            print("-" * 80)
            print(content)
            print("\n" + "="*80 + "\n")
            
    except Exception as e:
        print(f"❌ Database Error: {e}")

if __name__ == "__main__":
    export_posts()
