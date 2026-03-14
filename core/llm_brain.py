import ollama
import json
import sys

class LLMBrain:
    def __init__(self, model="mistral"):
        self.model = model
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running before proceeding."""
        try:
            ollama.list()
        except Exception as e:
            print("\n❌ CRITICAL ERROR: Ollama is not running!")
            print("   Please start Ollama in a separate terminal:")
            print("   $ ollama serve")
            print("\n   Then run this command again.\n")
            sys.exit(1)

    def think(self, prompt, system_role="You are a helpful AI assistant."):
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': system_role},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            print(f"\n❌ LLM Error: {e}")
            print("   Make sure Ollama is running: ollama serve\n")
            return None

    def think_json(self, prompt, system_role):
        """Forces JSON output."""
        full_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No Markdown."
        response = self.think(full_prompt, system_role)
        if not response:
            return {}
        try:
            # Clean up markdown if LLM adds it
            clean = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean)
        except:
            return {}