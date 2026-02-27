from core.registry import Registry
from core.llm_brain import LLMBrain

class ScoringAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_batch(status='UNDERSTOOD')
        if not tasks: return

        print(f"⚖️  SCORING AGENT: Filtering {len(tasks)} items...")
        for task in tasks:
            # STRICT Prompt
            prompt = f"""
            You are a strict VC Analyst. Score this article (0-100) on relevance to STARTUP INNOVATION and ENTREPRENEURSHIP.
            
            STRICT SCORING CRITERIA:
            - 90-100: Groundbreaking startup news, major VC funding >$10M, or new tactical framework for founders.
            - 70-89: Good startup advice or interesting seed round.
            - 50-69: General tech news (e.g., Apple released a phone) -> PENALIZE.
            - 0-49: Fluff, politics, general news, or "Top 10" lists.
            
            Title: {task['title']}
            Summary: {task['summary']}
            
            Return JSON ONLY: {{"score": <int>, "reason": "<string>"}}
            """
            
            result = self.brain.think_json(prompt, "You are a critical VC analyst.")
            score = result.get('score', 0)
            
            print(f"   Draft Score: {score} | {task['title'][:30]}...")
            
            self.registry.update_artifact(task['id'], {
                "score": score,
                "relevance_reasoning": result.get('reason', ''),
                "status": "SCORED"
            })