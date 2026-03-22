from core.registry import Registry
from core.llm_brain import LLMBrain

class UnderstandingAgent:
    def __init__(self):
        self.registry = Registry()
        self.brain = LLMBrain()

    def run(self):
        tasks = self.registry.fetch_smart_batch(status='DISCOVERED', limit=20)
        if not tasks: 
            print("No articles to understand.")
            return

        print(f"🧠 UNDERSTANDING AGENT: Extracting deeper insights from {len(tasks)} items...")
        for task in tasks:
            # Enhanced extraction prompt for structured insights
            prompt = f"""
            Identify the key business components from this article for a strategic database.
            
            ARTICLE TITLE: {task['title']}
            CONTENT: {task['raw_content'][:4500]}
            
            Identify and return in JSON format:
            1. company: Main company name (string)
            2. industry: Main industry category (string)
            3. strategy: 1-sentence description of their core strategic move or innovation (string)
            4. takeaways: 3 specific, actionable bullet points for a founder (list of strings)
            5. summary: A high-level 2-sentence summary (string)
            6. status: If this article contains a significant case study, set to 'HIGH_POTENTIAL', else set to 'UNDERSTOOD' (string)
            
            Return ONLY the JSON object.
            """
            
            try:
                # Use think_json for structured extraction
                analysis = self.brain.think_json(prompt, "You are a senior business research analyst specializing in extraction.")
                
                # Format a cleaner summary/insight for storage
                structured_summary = f"🏢 Company: {analysis.get('company', 'Unknown')}\n"
                structured_summary += f"💡 Core Strategy: {analysis.get('strategy', 'N/A')}\n"
                structured_summary += f"✅ Takeaways:\n"
                for t in analysis.get('takeaways', []):
                    structured_summary += f"   - {t}\n"
                structured_summary += f"\n📖 Summary: {analysis.get('summary', 'No summary available.')}"

                self.registry.update_artifact(task['id'], {
                    "summary": structured_summary,
                    "strategic_insight": analysis.get('strategy', ''), # Extra field match
                    "status": "UNDERSTOOD"
                })
                print(f"   ✅ Processed: {task['title'][:40]}...")
            except Exception as e:
                print(f"   ⚠️ Error processing task {task['id']}: {e}")
                # Baseline fallback to avoid stuck items
                self.registry.update_artifact(task['id'], { "status": "FAILED_UNDERSTANDING" })