from core.registry import Registry
from core.llm_brain import LLMBrain

class WriterAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_batch(status='INSIGHTS_READY')
        print(f"✍️ WRITER AGENT: Drafting content for {len(tasks)} items...")

        for task in tasks:
            prompt = f"""
            Write a viral LinkedIn post using these insights. 
            Use a hook, bullet points for the insights, and a call to action.
            
            Topic: {task['title']}
            Insights: {task['strategic_insight']}
            """
            
            post_content = self.brain.think(prompt, "You are a copywriter.")
            
            print(f"   Drafted post for: {task['title']}")
            print("-" * 20)
            print(post_content[:100] + "...") 
            print("-" * 20)
            
            self.registry.update_artifact(task['id'], {
                "final_post": post_content,
                "status": "PUBLISHED" # Or 'READY_FOR_REVIEW'
            })