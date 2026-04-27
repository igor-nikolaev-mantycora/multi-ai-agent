import json
from agents import ask_gpt

def consensus(answers):
    return ask_gpt(f"""
Answers:
{json.dumps(answers)}

Find consensus and best answer.
Return JSON with answer + confidence.
""")

def contradictions(answers):
    return ask_gpt(f"""
Answers:
{json.dumps(answers)}

List contradictions clearly.
""")

def weighted_scores(answers):
    return ask_gpt(f"""
Answers:
{json.dumps(answers)}

Score each:
- quality (0-10)
- confidence (0-1)

Return JSON.
""")