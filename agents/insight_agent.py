from core.registry import Registry
from core.llm_brain import LLMBrain

class InsightAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        # Fetch articles that have been SCORED
        tasks = self.registry.fetch_batch(status='SCORED', limit=30)
        if not tasks:
            print("No scored items to process.")
            return

        print(f"💡 INSIGHT AGENT: Processing {len(tasks)} items for strategic gems...")

        for task in tasks:
            # Skip low scores strictly
            if task['score'] < 65: # Tightened from 60
                self.registry.update_artifact(task['id'], {"status": "ARCHIVED_LOW_SCORE"})
                continue

            print(f"   Deriving deep insights for: {task['title']}...")
            
            prompt = f"""
            TASK: Transform this business report into a high-value strategic case study.
            
            ARTICLE: {task['title']}
            CONTEXT: {task['summary']}
            
            EXTRACT THE FOLLOWING (JSON ONLY):
            1. market_gap (string): The specific problem or market inefficiency they identified.
            2. strategy_pivot (string): The exact move, business model change, or tactical pivot that drove success.
            3. trade_offs (string): What did they sacrifice or ignore to win? (e.g., profitability for growth, or vice versa).
            4. unit_economics (string/null): Any mention of CAC, LTV, revenue, or margins if available.
            5. actionable_lesson (string): A "Founder Playbook" style takeaway.
            
            RULES:
            - NO FUZZY LANGUAGE. Be specific.
            - If details aren't in the article, state 'Not explicitly mentioned'.
            - Focus on 'The How' and 'The Why', not just 'The What'.
            """
            
            try:
                insights = self.brain.think_json(prompt, "You are a senior business strategist specializing in deep-dive case studies.")
                
                # Format for the writer agent and human reading
                formatted_insights = (
                    f"🎯 MARKET GAP: {insights.get('market_gap', 'N/A')}\n"
                    f"🚀 STRATEGY: {insights.get('strategy_pivot', 'N/A')}\n"
                    f"⚖️ TRADE-OFFS: {insights.get('trade_offs', 'N/A')}\n"
                    f"📈 ECONOMICS: {insights.get('unit_economics', 'N/A')}\n"
                    f"💡 LESSON: {insights.get('actionable_lesson', 'N/A')}"
                )
                
                self.registry.update_artifact(task['id'], {
                    "strategic_insight": formatted_insights,
                    "status": "INSIGHTS_READY"
                })
                print(f"      ✅ Strategy Ready: {task['title'][:40]}")
            except Exception as e:
                print(f"      ⚠️ Insight extraction failed for {task['id']}: {e}")
                self.registry.update_artifact(task['id'], { "status": "FAILED_INSIGHT" })