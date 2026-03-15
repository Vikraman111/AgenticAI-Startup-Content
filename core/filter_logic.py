import ollama
import json

class SmartFilter:
    def __init__(self, model="llama3.2:1b"):
        self.model = model
        # Fast-kill list to save CPU/Time
        self.blacklist = [
            "mattress", "sunscreen", "shaver", "exfoliator", "skincare", 
            "gift guide", "best deals", "shopping", "walmart", "target",
            "sports", "celebrity", "entertainment", "recipe", "diet"
        ]

    def is_relevant(self, title, summary=""):
        # STAGE 1: Immediate Rejection (Zero CPU cost)
        text_to_check = (title + " " + summary).lower()
        if any(word in text_to_check for word in self.blacklist):
            return False, 0

        # STAGE 2: LLM Validation (Contextual Intelligence)
        prompt = f"""
        TASK: Is this article relevant to BUSINESS TRENDS, GROWTH STRATEGIES, STARTUP ADVICE, or INDUSTRY INSIGHTS?
        
        ARTICLE TITLE: {title}
        SUMMARY: {summary[:200]}
        
        CRITERIA:
        - YES: Actionable business advice, growth tactics, market trends, industry shifts, company strategy changes, consumer behavior patterns, economic analysis, business innovations.
        - NO: Pure funding/raise announcements without deeper strategy, lifestyle products, sports, entertainment, politics, general celebrity news.
        
        ANSWER ONLY in JSON format: {{"relevant": true/false, "reason": "short explanation"}}
        """

        try:
            response = ollama.chat(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                format='json',
                options={'temperature': 0} # Keep it consistent
            )
            
            result = json.loads(response['message']['content'])
            return result.get("relevant", False), 100
        except Exception as e:
            print(f"      ⚠️ LLM Error: {e}. Falling back to 'False'.")
            return False, 0