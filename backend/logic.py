import json
from agents import ask_gpt


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def safe_answers(answers):
    """
    Ensure all answers are strings and remove errors
    """
    clean = {}
    for k, v in answers.items():
        if isinstance(v, dict) and "error" in v:
            continue
        if v is None:
            continue
        clean[k] = str(v)
    return clean


def fallback_consensus(answers):
    """
    Simple fallback: return longest answer (often most complete)
    """
    if not answers:
        return {"answer": "No valid answers", "confidence": 0}

    best = max(answers.items(), key=lambda x: len(x[1]))
    return {
        "answer": best[1],
        "confidence": 0.3,
        "method": "fallback_length"
    }


# ---------------------------------------------------------
# Consensus
# ---------------------------------------------------------

def consensus(answers):
    answers = safe_answers(answers)

    if len(answers) == 0:
        return {"error": "No valid answers"}

    try:
        prompt = f"""
You are evaluating multiple AI answers.

Answers:
{json.dumps(answers, indent=2)}

Tasks:
1. Identify common agreement
2. Identify major differences
3. Produce BEST final answer
4. Assign confidence (0-1)

Return STRICT JSON:
{{
  "answer": "...",
  "confidence": 0.0-1.0
}}
"""
        result = ask_gpt(prompt)

        # Try parsing JSON safely
        try:
            return json.loads(result)
        except Exception:
            return {"raw": result, "confidence": 0.5}

    except Exception as e:
        return fallback_consensus(answers)


# ---------------------------------------------------------
# Contradictions
# ---------------------------------------------------------

def contradictions(answers):
    answers = safe_answers(answers)

    if len(answers) < 2:
        return "Not enough data for contradiction analysis"

    try:
        prompt = f"""
Compare the following answers:

{json.dumps(answers, indent=2)}

List ONLY real contradictions.
Ignore wording differences.

Return bullet points.
"""
        return ask_gpt(prompt)

    except Exception:
        # fallback: simple heuristic
        return "Contradiction detection unavailable (fallback mode)"


# ---------------------------------------------------------
# Weighted scoring
# ---------------------------------------------------------

def weighted_scores(answers):
    answers = safe_answers(answers)

    if len(answers) == 0:
        return {"error": "No valid answers"}

    try:
        prompt = f"""
Evaluate each answer:

{json.dumps(answers, indent=2)}

For each model return:
- quality (0-10)
- confidence (0-1)

Return STRICT JSON:
{{
  "model_name": {{
    "quality": number,
    "confidence": number
  }}
}}
"""
        result = ask_gpt(prompt)

        try:
            return json.loads(result)
        except Exception:
            return {"raw": result}

    except Exception:
        # fallback scoring
        fallback = {}
        for k, v in answers.items():
            fallback[k] = {
                "quality": min(len(v) / 50, 10),
                "confidence": 0.3
            }
        return fallback