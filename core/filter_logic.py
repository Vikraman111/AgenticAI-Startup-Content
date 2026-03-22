import json
from core.llm_brain import LLMBrain

class SmartFilter:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.brain = LLMBrain(default_model=self.model)
        # Fast-kill list to save CPU/Time
        self.blacklist = [
            "mattress", "sunscreen", "shaver", "exfoliator", "skincare", 
            "gift guide", "best deals", "shopping", "walmart", "target",
            "sports", "celebrity", "entertainment", "recipe", "diet",
            "bras", "loafers", "boots", "rentals", "vacation", "photos",
            "tour", "how to watch", "live stream", "promo code", "coupons",
            "gift ideas", "amazon deals", "holiday", "travel guide"
        ]

    def is_relevant(self, title, summary=""):
        # STAGE 1: Immediate Rejection (Zero CPU cost)
        text_to_check = (title + " " + summary).lower()
        if any(word in text_to_check for word in self.blacklist):
            return False, 0

        # STAGE 2: LLM Validation (Contextual Intelligence)
        prompt = f"""
        TASK: Evaluate if this article is high-value for a BUSINESS STRATEGY & GROWTH audience.
        
        ARTICLE TITLE: {title}
        SUMMARY/SNIPPET: {summary[:300]}
        
        CRITERIA FOR 'TRUE':
        1. Deep Strategy: Case studies of how a company scaled, pivoted, or dominated a niche.
        2. Market Analysis: Identification of new market gaps, shifts in consumer behavior, or industry disruption.
        3. Operational Excellence: Specific tactics (marketing, product, sales) that led to measurable success.
        4. Founder Lessons: Post-mortems or success stories with actionable takeaways.
        
        CRITERIA FOR 'FALSE':
        1. General News: Mere funding rounds without strategic context, hiring news, or generic launches.
        2. Consumer Lifestyle: Product reviews, gift guides, general health/lifestyle advice.
        3. Noise: Politics, sports, celebrity gossip, generic motivational content.
        
        REJECTION GUIDELINE: If the article is just "Company X raised $Y million", it's usually FALSE unless the technology or market is revolutionary.
        
        RETURN JSON ONLY:
        {{
            "relevant": boolean,
            "confidence": int (0-100),
            "reason": "1-sentence explanation of the strategic value or why it was rejected"
        }}
        """

        try:
            result = self.brain.think_json(prompt, "You are a strict Business Strategy Filter. Your goal is to keep ONLY high-signal strategic content.")
            return result.get("relevant", False), result.get("confidence", 0)
        except Exception as e:
            print(f"      ⚠️ SmartFilter Error: {e}. Falling back to 'False'.")
            return False, 0