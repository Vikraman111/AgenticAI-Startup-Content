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
        You are a **Strategy Consultant** advising startup founders. Score this article (**0-100**) 
        on the quality of its BUSINESS TRENDS, GROWTH STRATEGIES, and ACTIONABLE ADVICE.
        
        ARTICLE TITLE: {task['title']}
        CONTENT SUMMARY: {task['summary']}
        
        SCORING CRITERIA (from e2e-local):
        - **90-100**: Deep strategic, actionable advice for startups, game-changing market trends, or clear growth patterns.
        - **70-89**: Solid market analysis, interesting growth strategies, clear lessons from successful startups.
        - **50-69**: Basic business news or high-level trends with limited actionable insight.
        - **0-49**: Routine funding rounds with no strategic context, PR announcements, or fluff.
        
        Format your response as a JSON object:
        {{
            "score": integer,
            "reasoning": "brief explanation"
        }}
        """
            
            try:
                result = self.brain.think_json(prompt, "You are a professional business strategy consultant.")
                final_score = result.get('score', 0)
                reasoning = result.get('reasoning', "N/A")
            except Exception as e:
                print(f"Error scoring task {task['id']}: {e}")
                final_score = 0
                reasoning = "Error in scoring"
            
            print(f"   Score: {final_score}/100 | {task['title'][:40]}...")
            
            self.registry.update_artifact(task['id'], {
                "score": final_score,
                "relevance_reasoning": result.get('reasoning', ''),
                "status": "SCORED"
            })