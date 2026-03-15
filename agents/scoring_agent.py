from core.registry import Registry
from core.llm_brain import LLMBrain

class ScoringAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_batch(status='UNDERSTOOD', limit=20)
        if not tasks: return

        print(f"⚖️  SCORING AGENT: Filtering {len(tasks)} items...")
        for task in tasks:
            # BUSINESS TREND ANALYSIS Prompt
            prompt = f"""
            You are a Strategy Consultant advising startup founders. Score this article (0-100) on the quality of its BUSINESS TRENDS, GROWTH STRATEGIES, and ACTIONABLE ADVICE.
            
            SCORING CRITERIA:
            - 90-100: Deep strategic, actionable advice for startups, game-changing market trends, novel growth tactics, or clear patterns that affect multiple sectors.
            - 70-89: Solid market analysis, interesting growth strategies, good industry insights, clear lessons from successful (or failed) startups.
            - 50-69: Basic business news or high-level trends with limited actionable insight.
            - 0-49: Routine funding rounds with no strategic context, PR announcements, fluff, or generic commentary.
            
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