BASE_PROMPT = "Answer clearly and accurately."

def tune_prompt(question):
    """
    Simple adaptive prompt tuning
    """
    if "math" in question.lower():
        return BASE_PROMPT + " Show step-by-step reasoning."
    if "why" in question.lower():
        return BASE_PROMPT + " Explain causality."
    if "compare" in question.lower():
        return BASE_PROMPT + " Provide structured comparison."
    return BASE_PROMPT