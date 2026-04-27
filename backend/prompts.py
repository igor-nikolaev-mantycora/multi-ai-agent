BASE = "Answer clearly and accurately."

def tune_prompt(q):
    ql = q.lower()
    if "math" in ql:
        return BASE + " Show step-by-step reasoning."
    if "compare" in ql:
        return BASE + " Use structured comparison."
    if "why" in ql:
        return BASE + " Explain causality."
    return BASE