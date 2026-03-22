import os
import json
import sys
from openai import OpenAI
from dotenv import load_dotenv
from core.tracker import TokenTracker

# Load environment variables
load_dotenv()

class LLMBrain:
    def __init__(self, default_model="gpt-4o-mini"):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("\n❌ CRITICAL ERROR: OPENAI_API_KEY not found in .env!")
            print("   Please add your key: OPENAI_API_KEY=sk-xxxx\n")
            sys.exit(1)
            
        self.client = OpenAI(api_key=api_key)
        self.default_model = default_model
        # print(f"🌐 LLM BRAIN: Connected to OpenAI (Default: {self.default_model})")

    def think(self, prompt, system_role="You are a helpful AI assistant.", model=None):
        """Standard text completion."""
        target_model = model if model else self.default_model
        try:
            response = self.client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7
            )
            
            # Log usage
            usage = response.usage
            TokenTracker.log_usage(target_model, usage.prompt_tokens, usage.completion_tokens)
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"\n❌ OpenAI Error: {e}")
            return None

    def think_json(self, prompt, system_role, model=None):
        """Forces JSON output using OpenAI's response_format."""
        target_model = model if model else self.default_model
        try:
            response = self.client.chat.completions.create(
                model=target_model,
                messages=[
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0
            )
            
            # Log usage
            usage = response.usage
            TokenTracker.log_usage(target_model, usage.prompt_tokens, usage.completion_tokens)
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"⚠️ OpenAI JSON Error: {e}")
            return {}