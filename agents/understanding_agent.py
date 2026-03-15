from core.registry import Registry
from core.llm_brain import LLMBrain

class UnderstandingAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_smart_batch(status='DISCOVERED', limit=20)
        if not tasks: 
            print("No articles to understand.")
            return

        print(f"🧠 UNDERSTANDING AGENT: Processing {len(tasks)} items...")
        for task in tasks:
            prompt = f"""
            Summarize this article in 2-3 sentences. Identify the key company, funding amount (if any), and main innovation.
            TEXT: {task['raw_content'][:3500]}
            """
            analysis = self.brain.think(prompt, "You are a concise editor.")
            
            self.registry.update_artifact(task['id'], {
                "summary": analysis,
                "status": "UNDERSTOOD"
            })