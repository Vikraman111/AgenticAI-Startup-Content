from core.registry import Registry
from core.llm_brain import LLMBrain

class ScoringAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_batch(status='UNDERSTOOD', limit=20)
        if not tasks: return

        print(f"⚖️  SCORING AGENT: Rating {len(tasks)} items...")
        for task in tasks:
            # QUALITY FOCUS Prompt
            prompt = f"""
            Identify the strategic intelligence in this article for a business founder/investor. 
            Article Title: {task['title']}
            Content Summary: {task['summary']}

            Rate the following on a scale of 0 to 10:
            1. STRATEGIC_INSIGHT: Does it detail 'The Why' behind a success or failure? Does it explain a complex tactic (e.g., SEO arbitrage, unique supply chain pivot)?
            2. NOVELTY: Is this a unique insight or a market gap that others haven't seen? (10=Unique/Rare, 0=Common News)
            3. ACTIONABILITY: Could a founder take this specific strategy and apply it today?

            CRITICAL SCORING RULES:
            - Standard PR/Funding/Hiring: MAX 3 points.
            - Deep Dive/Case Study: MIN 7 points.
            - Filler/Generic advice: MAX 2 points.

            Return JSON ONLY: {{
                "strategic_insight": <int>, 
                "novelty": <int>, 
                "actionable": <int>, 
                "reasoning": "<string if this scored > 70 or < 30>"
            }}
            """
            
            result = self.brain.think_json(prompt, "You are a professional business strategist.")
            
            # Weighted calculation: (Insight*4) + (Novelty*3) + (Actionable*3) = Max 100
            s = result.get('strategic_insight', 0)
            n = result.get('novelty', 0)
            a = result.get('actionable', 0)
            
            final_score = (s * 4) + (n * 3) + (a * 3)
            
            print(f"   Score: {final_score}/100 | {task['title'][:40]}...")
            
            self.registry.update_artifact(task['id'], {
                "score": final_score,
                "relevance_reasoning": result.get('reasoning', ''),
                "status": "SCORED"
            })