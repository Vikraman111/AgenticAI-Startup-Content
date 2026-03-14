#!/usr/bin/env python3
"""
MAIN ORCHESTRATOR: Runs the complete AI-Agentic pipeline
Processes articles through all stages: Monitor → Understand → Score → Insights → Write
"""

import sqlite3
import sys
from run_monitoring import run_monitoring
from run_understanding import run_understanding
from run_scoring import run_scoring
from run_insights import run_insights
from run_writer import run_writer

def purge_junk():
    """Remove low-quality/junk articles from database."""
    try:
        conn = sqlite3.connect('data/agent_registry.db')
        cursor = conn.cursor()
        
        # Delete anything containing lifestyle keywords
        junk_words = ['mattress', 'shaver', 'sunscreen', 'walmart', 'exfoliator']
        for word in junk_words:
            cursor.execute("DELETE FROM artifacts WHERE title LIKE ?", (f'%{word}%',))
        
        conn.commit()
        removed = conn.total_changes
        conn.close()
        
        if removed > 0:
            print(f"🧹 Purged {removed} junk entries from database.")
        return removed
    except Exception as e:
        print(f"⚠️  Could not purge junk: {e}")
        return 0

def run_pipeline(stages=None):
    """
    Run the complete pipeline or selected stages.
    
    Args:
        stages: List of stages to run. If None, runs all.
                Options: 'monitor', 'understand', 'score', 'insights', 'writer'
    """
    
    if stages is None:
        stages = ['monitor', 'understand', 'score', 'insights', 'writer']
    
    print("\n" + "="*80)
    print("🚀 AI-AGENTIC ORCHESTRATOR")
    print("="*80)
    print(f"Running stages: {', '.join(stages).upper()}\n")
    
    try:
        if 'monitor' in stages:
            run_monitoring()
            purge_junk()
        
        if 'understand' in stages:
            run_understanding()
        
        if 'score' in stages:
            run_scoring()
        
        if 'insights' in stages:
            run_insights()
        
        if 'writer' in stages:
            run_writer()
        
        print("\n" + "="*80)
        print("✅ PIPELINE COMPLETE!")
        print("="*80)
        print("\n📊 View results with: python3 tools/review_dashboard.py\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Pipeline error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Agentic Pipeline Orchestrator")
    parser.add_argument(
        "--stages",
        nargs="+",
        choices=['monitor', 'understand', 'score', 'insights', 'writer'],
        help="Stages to run (default: all)"
    )
    parser.add_argument(
        "--purge-only",
        action="store_true",
        help="Only purge junk articles and exit"
    )
    
    args = parser.parse_args()
    
    if args.purge_only:
        print("🧹 Purging junk articles...")
        purge_junk()
        print("Done!")
    else:
        run_pipeline(args.stages)