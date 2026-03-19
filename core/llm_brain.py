import ollama
import json
import sys

class LLMBrain:
    def __init__(self, model="mistral"):
        self.model_name = model
        print(f"🏠 LLM BRAIN: Using Local Ollama ( {self.model_name} )")
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running before proceeding."""
        try:
            ollama.list()
        except Exception as e:
            print("\n❌ CRITICAL ERROR: Ollama is not running!")
            print("   Please start Ollama in a separate terminal:")
            print("   $ ollama serve\n")
            sys.exit(1)

    def think(self, prompt, system_role="You are a helpful AI assistant."):
        try:
            # Ollama chat
            response = ollama.chat(model=self.model_name, messages=[
                {'role': 'system', 'content': system_role},
                {'role': 'user', 'content': prompt},
            ])
            return response['message']['content']
        except Exception as e:
            print(f"\n❌ Ollama Error: {e}")
            return None

    def think_json(self, prompt, system_role):
        """Forces JSON output."""
        full_prompt = prompt + "\n\nIMPORTANT: Return ONLY valid JSON. No Markdown formatting or preamble."
        response = self.think(full_prompt, system_role)
        if not response: 
            return {}
        try:
            # Clean up markdown if LLM adds it
            clean = response.replace("```json", "").replace("```", "").strip()
            if clean.startswith("```"):
                clean = clean.strip("`").strip()
            return json.loads(clean)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
            return {}