#!/usr/bin/env python3
"""
STAGE 2: Understanding & Summarization
Analyzes raw content and creates summaries.
"""

from agents.understanding_agent import UnderstandingAgent

def run_understanding():
    print("\n" + "="*80)
    print("🧠 UNDERSTANDING STAGE: Summarizing Articles")
    print("="*80 + "\n")
    
    agent = UnderstandingAgent()
    agent.run()
    
    print("\n✅ Understanding complete.")

if __name__ == "__main__":
    run_understanding()
