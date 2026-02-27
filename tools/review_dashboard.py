import sys
import os

# --- PATH FIX: Allow importing from parent directory ---
# This adds the project root folder to Python's search path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# -------------------------------------------------------

from core.registry import Registry

def show_dashboard():
    reg = Registry()
    
    # 1. Check if DB is empty
    try:
        items = reg.get_all_scored()
    except Exception as e:
        print(f"❌ Database Error: {e}")
        print("Tip: Delete 'data/agent_registry.db' and run main_orchestrator.py again.")
        return

    if not items:
        print("\n📭 Database is empty or no articles have been SCORED yet.")
        print("   (Run main_orchestrator.py first)")
        return

    print("\n" + "="*100)
    print(f"📊 REVIEW DASHBOARD ({len(items)} Scored Items)")
    print("="*100)
    
    # Header
    print(f"{'SCORE':<6} | {'SOURCE':<25} | {'TITLE':<50}")
    print("-" * 100)
    
    for item in items:
        score = item['score']
        
        # Color Coding
        if score >= 90: mark = "🔥"    # Hot/Viral
        elif score >= 70: mark = "🟢"  # Good
        elif score >= 50: mark = "🟡"  # Average
        else: mark = "🔴"              # Low Quality
        
        # Clean Source Name
        src = item['source_module'].replace("_Crawler", "")[:25]
        
        print(f"{mark} {score:<3} | {src:<25} | {item['title'][:50]}...")
        
        if score >= 70:
             print(f"      🔗 Link: {item['url']}")
             print(f"      💡 Reasoning: {item['relevance_reasoning'][:120]}...")
             print("-" * 40)

    print("\n")

if __name__ == "__main__":
    show_dashboard()