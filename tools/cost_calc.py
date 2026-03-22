import json
import os
import sys

# Price per 1M tokens (USD) - Standard OpenAI pricing as of early 2024
PRICING = {
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4o": {"input": 5.00, "output": 15.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}

# Approx USD to INR
EXCHANGE_RATE = 83.0

USAGE_FILE = "data/usage_log.json"

def calculate_costs():
    if not os.path.exists(USAGE_FILE):
        print("❌ No usage data found. Run the pipeline first.")
        return

    with open(USAGE_FILE, 'r') as f:
        data = json.load(f)

    print("\n" + "="*50)
    print("💰 AI-AGENTIC COST CALCULATION")
    print("="*50)
    
    total_usd = 0.0
    
    # Detailed breakdown by STAGE
    stage_usage = {}
    for call in data.get("calls", []):
        stage = call.get("stage", "Unknown")
        model = call["model"]
        if stage not in stage_usage:
            stage_usage[stage] = {"p": 0, "c": 0, "cost": 0.0}
        
        price = PRICING.get(model, PRICING["gpt-4o-mini"])
        icost = (call["p_tokens"] / 1_000_000) * price["input"]
        ocost = (call["c_tokens"] / 1_000_000) * price["output"]
        
        stage_usage[stage]["p"] += call["p_tokens"]
        stage_usage[stage]["c"] += call["c_tokens"]
        stage_usage[stage]["cost"] += (icost + ocost)

    for stage, usage in stage_usage.items():
        total_usd += usage["cost"]
        mark = "✍️" if stage == "Writer" else "⚙️"
        print(f"\n{mark} Stage: {stage}")
        print(f"   Prompt:     {usage['p']:>8} tokens")
        print(f"   Completion: {usage['c']:>8} tokens")
        print(f"   Cost:       ${usage['cost']:.4f}")

    total_inr = total_usd * EXCHANGE_RATE

    print("\n" + "-"*50)
    print(f"💎 TOTAL BUDGET SPENT")
    print(f"   USD:  ${total_usd:.4f}")
    print(f"   INR:  ₹{total_inr:.2f}")
    print("-" * 50 + "\n")

if __name__ == "__main__":
    calculate_costs()
