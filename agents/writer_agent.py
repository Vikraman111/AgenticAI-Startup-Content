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
            # The audience/ reader profile will be business leaders entrepreneurs, startup founders and aspiring founders -- 1
            # Word limit - Ideal - 180 - Max limit - 225 Min - 150
            prompt = f"""
Write a LinkedIn post based on the business insight provided.


**MANDATORY STRICT RULES** 

- Ensure small paragraphs are maintained and word limit is not exceeded. The content should be a mix of bulletin points whenever needed along with a short paragraph style content to ensure easy readability and promote engagement.
- Have catchy headers for bulletin points along with an emoji and bolded start (not to be done every paragraph but whenever it feels required).
- Do not mention attention grabbing  opening, just have a nice opening thats it.
- Optimize content for the best readability and engagement.

CONTENT STYLE
- Write in a strong storytelling narrative.
- Start with a powerful hook statement in the first line.
- Use simple English
- Highly engaging language.
- The tone must feel like it is written by a founder sharing a business insight.
- The writing must sound human and natural, not robotic or like a news report.

CONTENT RULES
- DO NOT copy the article text or sentences.
- Have shorter paragraphs and bulleted points for ease of reading.
- The content must be fact-oriented and based only on the insight provided.
- Do NOT fabricate or assume information not present in the breakdown.
- Frame the post as a strategic business insight or founder lesson.

INSIGHT REQUIREMENTS
The post must clearly highlight at least one of the following:
- How the company identified a market gap
- What they did differently from competitors
- A key risk they identified and how they mitigated it
- Their unique positioning
- The key success factor behind their growth

AUDIENCE
- Business leaders
- Entrepreneurs
- Startup founders
- Aspiring Entrepreneurs

STRUCTURE
1. Hook statement (attention-grabbing opening)
2. Short narrative explaining the situation
3. Strategic insight or lesson from the case
4. Clear takeaway for founders

WORD LIMIT
- Ideal: 180 words
- Minimum: 150 words
- Maximum: 225 words

For reference, the founder's previous articles define the tone and writing style. Follow that tone (founder-like, reflective, and insight-driven), but still strictly follow all the structure and rules mentioned above.

Topic: {task['title']}
Business Breakdown: {task['strategic_insight']}
"""
            post_content = self.brain.think(prompt, "You are an elite B2B Ghostwriter for startup founders and investors.")
            
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