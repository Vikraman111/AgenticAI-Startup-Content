from core.registry import Registry
from core.llm_brain import LLMBrain

class InsightAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        # We fetch SCORED items, but we filter inside loop for high scores
        tasks = self.registry.fetch_batch(status='SCORED')
        print(f"💡 INSIGHT AGENT: Looking for gems in {len(tasks)} items...")

        for task in tasks:
            if task['score'] < 70:
                # Mark as processed but ignored (Low Quality)
                self.registry.update_artifact(task['id'], {"status": "ARCHIVED_LOW_SCORE"})
                continue

            print(f"   Deriving insights for: {task['title']}...")
            
            prompt = f"""
            This article is high quality. Generate 3 specific "Actionable Takeaways" 
            for a startup founder based on this news.
            
            Article: {task['title']}
            Summary: {task['summary']}
            """
            
            insights = self.brain.think(prompt, "You are a Startup Advisor.")
            
            self.registry.update_artifact(task['id'], {
                "strategic_insight": insights,
                "status": "INSIGHTS_READY"
            })