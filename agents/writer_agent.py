import sys
import os

# Add project root to path so we can import 'core'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.registry import Registry
from core.llm_brain import LLMBrain
class WriterAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self, limit=5):
        tasks = self.registry.fetch_batch(status='INSIGHTS_READY', limit=limit)
        print(f"✍️ WRITER AGENT: Drafting content for {len(tasks)} items...")

        for task in tasks:
            # Clean up the source name (e.g., 'TechCrunch_Crawler' -> 'TechCrunch')
            source = task.get('source_module', 'Unknown').split('_')[0].strip()
            
            prompt = f"""
Write a high-impact LinkedIn post based on the business insight provided.

**MANDATORY STYLE RULES**
- **MAX 1 SENTENCE PER PARAGRAPH**. Use frequent line breaks.
- Use a "Founder/Investor" tone: reflective, data-driven, yet conversational.
- NO fluff or corporate-speak (avoid: "leverage", "robust", "synergy", "game-changer").
- Use bold headers for key sections.
- Use relevant emojis sparingly but effectively to highlight points.

**WORD LIMITS**
- Minimum: 120 words
- Maximum: 200 words
- Ideal: 160 words (excluding credits)

**STRUCTURE**
1. **Hook**: A provocative or counter-intuitive first line.
2. **The Context**: 2-3 single-sentence paragraphs explaining the situation.
3. **Strategic Breakdown**: Use a bulleted list with bolded category names.
4. **Founder Advice**: One-sentence direct takeaway.
5. **Engagement**: A tactical question for the audience.
6. **Source Credits**: At the very end, add the line "Credits: {source}" (Example: Credits: Forbes). No URLs.

Topic: {task['title']}
Business Case Study: {task['strategic_insight']}
"""
            post_content = self.brain.think(
                prompt=prompt, 
                system_role="You are an elite B2B Ghostwriter for startup founders and investors.",
                model="gpt-4o-mini"
            )
            
            if not post_content:
                print(f"   ⚠️ Skipping {task['title']} due to LLM error.")
                continue

            print(f"   Drafted post for: {task['title']}")
            print("-" * 20)
            print(post_content[:100] + "...") 
            print("-" * 20)
            
            self.registry.update_artifact(task['id'], {
                "final_post": post_content,
                "status": "WRITTEN"
            })

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run the Writer Agent directly.")
    parser.add_argument("--limit", type=int, default=5, help="Number of posts to generate.")
    args = parser.parse_args()
    
    agent = WriterAgent()
    agent.run(limit=args.limit)