import os
import json
import sys
import ollama
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class LLMBrain:
    def __init__(self, model="gemini-1.5-flash"):
        self.gemini_key = os.environ.get("GEMINI_API_KEY")
        self.model_name = model
        
        if self.gemini_key:
            print(f"✨ LLM BRAIN: Using Google Gemini ({self.model_name})")
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel(self.model_name)
        else:
            print("🏠 LLM BRAIN: Using Local Ollama (mistral)")
            self.model_name = "mistral"
            self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running before proceeding."""
        try:
            ollama.list()
        except Exception as e:
            print("\n❌ CRITICAL ERROR: Ollama is not running and no GEMINI_API_KEY found!")
            print("   Please start Ollama in a separate terminal:")
            print("   $ ollama serve")
            print("   OR add GEMINI_API_KEY to your .env file.\n")
            sys.exit(1)

    def think(self, prompt, system_role="You are a helpful AI assistant."):
        try:
            if self.gemini_key:
                # Gemini combined role + prompt
                full_prompt = f"System Role: {system_role}\n\nUser Request: {prompt}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text
            else:
                # Ollama chat
                response = ollama.chat(model=self.model_name, messages=[
                    {'role': 'system', 'content': system_role},
                    {'role': 'user', 'content': prompt},
                ])
                return response['message']['content']
        except Exception as e:
            print(f"\n❌ LLM Error: {e}")
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
            return json.loads(clean)
        except Exception as e:
            print(f"⚠️ JSON Parse Error: {e}")
            return {}