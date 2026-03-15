from core.registry import Registry
from core.llm_brain import LLMBrain

class InsightAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        # We fetch SCORED items, but we filter inside loop for high scores
        tasks = self.registry.fetch_batch(status='SCORED', limit=20)
        print(f"💡 INSIGHT AGENT: Looking for gems in {len(tasks)} items...")

        for task in tasks:
            if task['score'] < 70:
                # Mark as processed but ignored (Low Quality)
                self.registry.update_artifact(task['id'], {"status": "ARCHIVED_LOW_SCORE"})
                continue

            print(f"   Deriving insights for: {task['title']}...")
            
            prompt = f"""
            You are a top-tier Strategic Consultant and Business Analyst. 
            Do NOT simply summarize the article. Instead, breakdown the core business case study based PURELY ON FACTS from the article.
            
            Identify and extract:
            1. The Market Gap: What specific problem or whitespace did the company identify?
            2. The Strategic Differentiator: EXACTLY what did they do differently to succeed?
            3. Risks & Tradeoffs: What risks did they take, or what conventional wisdom did they ignore?
            4. The Core Lesson: Actionable takeaway for a founder.
            
            Keep the tone professional, objective, and deeply analytical.
            
            Article: {task['title']}
            Summary/Content: {task['summary']}
            """
            
            insights = self.brain.think(prompt, "You are a Strategic Business Analyst.")
            
            self.registry.update_artifact(task['id'], {
                "strategic_insight": insights,
                "status": "INSIGHTS_READY"
            })