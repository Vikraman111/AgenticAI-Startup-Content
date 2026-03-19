#!/usr/bin/env python3
"""
STAGE 3: Scoring & Filtering
Rates articles based on business trends relevance.
"""

from agents.scoring_agent import ScoringAgent

def run_scoring():
    print("\n" + "="*80)
    print("⚖️  SCORING STAGE: Rating Business Trend Quality")
    print("="*80 + "\n")
    
    agent = ScoringAgent()
    agent.run()
    
    print("\n✅ Scoring complete.")
    print("👉 Next Step: python3 run_insights.py")

if __name__ == "__main__":
    run_scoring()
