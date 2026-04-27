import datetime
import json
from pathlib import Path

def estimate_cost(text, price_per_token=0.00001):
    tokens = len(text.split())
    return round(tokens * price_per_token, 6)

def save_log(data):
    log_dir = Path(__file__).resolve().parent / "logs"
    log_dir.mkdir(exist_ok=True)
    fname = log_dir / f"log_{datetime.datetime.now().timestamp()}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
