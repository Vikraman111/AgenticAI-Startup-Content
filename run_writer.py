#!/usr/bin/env python3
"""
STAGE 5: Content Writing
Generates final content (LinkedIn posts, etc.) from insights.
"""

import argparse
from agents.writer_agent import WriterAgent

def run_writer(limit=5):
    print("\n" + "="*80)
    print("✍️  WRITER STAGE: Generating Final Content")
    print("="*80 + "\n")
    
    agent = WriterAgent()
    agent.run(limit=limit)
    
    print("\n✅ Content writing complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate final content from insights.")
    parser.add_argument("--limit", type=int, default=5, help="Number of articles to write posts for (default: 5)")
    args = parser.parse_args()
    
    run_writer(limit=args.limit)
