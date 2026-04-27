import os, json, datetime

def estimate_cost(text, price_per_token=0.00001):
    tokens = len(text.split())
    return tokens * price_per_token

def save_log(data):
    os.makedirs("logs", exist_ok=True)
    fname = f"logs/log_{datetime.datetime.now().timestamp()}.json"
    with open(fname, "w") as f:
        json.dump(data, f, indent=2)