#!/usr/bin/env python3
"""
STAGE 4: Insight Generation
Extracts actionable insights from high-quality articles.
"""

from agents.insight_agent import InsightAgent

def run_insights():
    print("\n" + "="*80)
    print("💡 INSIGHTS STAGE: Extracting Actionable Insights")
    print("="*80 + "\n")
    
    agent = InsightAgent()
    agent.run()
    
    print("\n✅ Insights extraction complete.")
    print("👉 Next Step: python3 run_writer.py")

if __name__ == "__main__":
    run_insights()
