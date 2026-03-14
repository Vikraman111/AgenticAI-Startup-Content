#!/usr/bin/env python3
"""
STAGE 5: Content Writing
Generates final content (LinkedIn posts, etc.) from insights.
"""

from agents.writer_agent import WriterAgent

def run_writer():
    print("\n" + "="*80)
    print("✍️ WRITER STAGE: Generating Final Content")
    print("="*80 + "\n")
    
    agent = WriterAgent()
    agent.run()
    
    print("\n✅ Content writing complete.")

if __name__ == "__main__":
    run_writer()
