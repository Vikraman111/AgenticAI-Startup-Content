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
            prompt = f"""
            Write a highly engaging, thought-provoking LinkedIn post based on the following strategic business breakdown. 
            
            RULES:
            - DO NOT copy the article text or sound like a news reporter.
            - Frame this as a "Business Case Study" or "Strategic Lesson".
            - Highlight the specific Market Gap they found.
            - Explain the exact reason for their success/failure based on the facts provided.
            - Include the Core Lesson or risk taken.
            - Format in a highly readable, engaging way (use a strong hook, bullet points for the breakdown, and a thought-provoking closing question).
            
            Topic: {task['title']}
            Business Breakdown: {task['strategic_insight']}
            """
            
            post_content = self.brain.think(prompt, "You are an elite B2B Ghostwriter for startup founders and investors.")
            
            print(f"   Drafted post for: {task['title']}")
            print("-" * 20)
            print(post_content[:100] + "...") 
            print("-" * 20)
            
            self.registry.update_artifact(task['id'], {
                "final_post": post_content,
                "status": "PUBLISHED" # Or 'READY_FOR_REVIEW'
            })