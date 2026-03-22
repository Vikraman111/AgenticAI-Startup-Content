import json
import numpy as np
from core.llm_brain import LLMBrain

# STRATEGIC ANCHOR: Copied from GitHub "e2e-local" standards
# Focus: Actionable business advice, growth tactics, market disruption, market gaps, leadership, failed startup post-mortems.
ANCHOR_DESCRIPTION = """
Actionable business trends, growth strategies, startup advice, industry insights, 
market shifts, innovation, leadership lessons, failed startup post-mortems, 
market gaps, and tactical execution for founders.
"""

class SmartFilter:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.brain = LLMBrain(default_model=self.model)
        self._anchor_vector = None # Cached vector
        
        # Fast-kill list (Zero cost)
        self.blacklist = [
            "mattress", "sunscreen", "shaver", "exfoliator", "skincare", 
            "gift guide", "best deals", "shopping", "walmart", "target",
            "sports", "celebrity", "entertainment", "recipe", "diet",
            "bras", "loafers", "boots", "rentals", "vacation", "photos",
            "tour", "how to watch", "live stream", "promo code", "coupons",
            "amazon deals", "holiday", "travel guide"
        ]
        
        # High-priority words that "Force-Pass" the semantic gate
        self.relevance_boost = [
            "strategy", "growth", "founder", "market gap", "scale", 
            "innovation", "tactics", "pivot", "disruption", "lesson",
            "hiring", "startup", "failure", "acquisition", "moat"
        ]

    def _cosine_similarity(self, v1, v2):
        if not v1 or not v2: return 0
        v1, v2 = np.array(v1), np.array(v2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def get_strategic_score(self, text):
        if not self._anchor_vector:
            self._anchor_vector = self.brain.get_embedding(ANCHOR_DESCRIPTION)
        target_vector = self.brain.get_embedding(text)
        return self._cosine_similarity(self._anchor_vector, target_vector)

    def is_relevant(self, title, summary=""):
        """
        Triple-Layer Filtering logic (Hybrid Efficiency).
        Ensures e2e-local quality with Semantic pass.
        """
        
        # LAYER 1: Blacklist
        text_to_check = (title + " " + summary).lower()
        if any(word in text_to_check for word in self.blacklist):
            return False, 0

        # LAYER 2: Semantic PASS (Threshold: 0.15 - very generous)
        sim_score = self.get_strategic_score(title)
        
        # Force-Pass if boost keyword found
        is_boosted = any(word in title.lower() for word in self.relevance_boost)
        
        if sim_score < 0.15 and not is_boosted:
            return False, int(sim_score * 100)

        # LAYER 3: LLM Validation (The 'Strategic Consultant' from GitHub)
        prompt = f"""
        TASK: Is this article relevant to BUSINESS TRENDS, GROWTH STRATEGIES, STARTUP ADVICE, or INDUSTRY INSIGHTS?
        
        TITLE: {title}
        CONTENT PREVIEW: {summary[:500]}
        
        CRITERIA (from e2e-local):
        - YES: Actionable business advice, growth tactics, market trends, strategy shifts, innovation, market gaps, leadership lessons, failed startup post-mortems.
        - LOW PRIORITY: Pure funding rounds or 'raise' news (unless it's a major pivot).
        - NO: Consumer lifestyle, celebrity news, sports, entertainment, or basic politics.
        
        RESPONSE FORMAT (Strict JSON):
        {{
            "relevant": boolean,
            "confidence": integer (0-100),
            "reason": string
        }}
        """
        
        try:
            response = self.brain.think_json(prompt, "You are a strict Strategy Consultant, evaluating content for actionable business insights.")
            return response.get('relevant', False), response.get('confidence', 0)
        except Exception as e:
            print(f"      ⚠️ SmartFilter Error: {e}. Falling back to 'False'.")
            return False, 0