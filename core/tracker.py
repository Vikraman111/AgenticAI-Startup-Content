import json
import os

USAGE_FILE = "data/usage_log.json"

class TokenTracker:
    @staticmethod
    def reset():
        """Resets the usage tracking file for a new run."""
        initial_data = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
            "calls": []
        }
        os.makedirs(os.path.dirname(USAGE_FILE), exist_ok=True)
        with open(USAGE_FILE, 'w') as f:
            json.dump(initial_data, f, indent=4)

    _current_stage = "Unknown"

    @staticmethod
    def set_stage(stage):
        """Sets the current orchestration stage to tag logs."""
        TokenTracker._current_stage = stage

    @staticmethod
    def log_usage(model, prompt_tokens, completion_tokens):
        """Logs usage from an LLM call."""
        if not os.path.exists(USAGE_FILE):
            TokenTracker.reset()
            
        with open(USAGE_FILE, 'r') as f:
            data = json.load(f)
            
        data["prompt_tokens"] += prompt_tokens
        data["completion_tokens"] += completion_tokens
        data["total_tokens"] += (prompt_tokens + completion_tokens)
        
        # Track detailed breakdown
        data["calls"].append({
            "stage": TokenTracker._current_stage,
            "model": model,
            "p_tokens": prompt_tokens,
            "c_tokens": completion_tokens
        })
        
        with open(USAGE_FILE, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def get_summary():
        """Returns the current accumulated usage."""
        if not os.path.exists(USAGE_FILE):
            return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        with open(USAGE_FILE, 'r') as f:
            return json.load(f)
