import json

def consensus_vote(answers):
    """
    Ask GPT to compare all answers and pick consensus
    """
    from agents import ask_gpt

    prompt = f"""
Compare these answers:

{json.dumps(answers, indent=2)}

Tasks:
1. Identify agreements
2. Identify disagreements
3. Select best answer OR synthesize new one

Return JSON:
{{
 "consensus": "...",
 "confidence": 0-1
}}
"""
    return ask_gpt(prompt)


def detect_contradictions(answers):
    from agents import ask_gpt

    prompt = f"""
Find contradictions between these answers:

{json.dumps(answers, indent=2)}

Return bullet list of conflicts.
"""
    return ask_gpt(prompt)