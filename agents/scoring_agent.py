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
            # BUSINESS TREND ANALYSIS Prompt
            prompt = f"""
            You are a Business Analyst. Score this article (0-100) on quality of BUSINESS TRENDS, MARKET INSIGHTS, and ACTIONABLE ANALYSIS.
            
            SCORING CRITERIA:
            - 90-100: Game-changing market trends, novel industry shift, deep analysis with implications, patterns that affect multiple sectors.
            - 70-89: Solid market analysis, interesting business patterns, good industry insights, startup strategy lessons.
            - 50-69: Basic business news but limited insight, generic commentary.
            - 0-49: Fluff, no real analysis, predictions without backing.
            
            Title: {task['title']}
            Summary: {task['summary']}
            
            Return JSON ONLY: {{"score": <int>, "reason": "<string>"}}
            """
            
            result = self.brain.think_json(prompt, "You are a business analyst focused on market trends.")
            score = result.get('score', 0)
            
            print(f"   Score: {score} | {task['title'][:40]}...")
            
            self.registry.update_artifact(task['id'], {
                "score": score,
                "relevance_reasoning": result.get('reason', ''),
                "status": "SCORED"
            })