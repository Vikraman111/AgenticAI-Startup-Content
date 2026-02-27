import ollama
import json

class LLMBrain:
    def __init__(self, model="mistral"):
        self.model = model

    def think(self, prompt, system_role="You are a helpful AI assistant."):
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_role},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return None

    def think_json(self, prompt, system_role):
        """Forces JSON output."""
        full_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No Markdown."
        response = self.think(full_prompt, system_role)
        try:
            # Clean up markdown if LLM adds it
            clean = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            return {}