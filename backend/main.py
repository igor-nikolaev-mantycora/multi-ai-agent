from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents import ask_gpt, ask_gemini, ask_grok, ask_claude
from logic import consensus, contradictions, weighted_scores
from prompts import tune_prompt
from utils import estimate_cost, save_log


app = FastAPI(title="Multi-AI Agent Backend", version="1.0")


# ---------------------------------------------------------
# CORS (required for frontend)
# ---------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # restrict later if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# Root route
# ---------------------------------------------------------
@app.get("/")
def root():
    return {
        "status": "backend running",
        "message": "Multi-AI Agent API"
    }


# ---------------------------------------------------------
# Health check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"ok": True}


# ---------------------------------------------------------
# Safe text extraction (prevents crashes)
# ---------------------------------------------------------
def safe_text(value):
    if isinstance(value, dict):
        return value.get("error", str(value))
    if value is None:
        return ""
    return str(value)


# ---------------------------------------------------------
# Parallel execution helper
# ---------------------------------------------------------
def run_parallel(prompt: str):
    tasks = {
        "gpt": ask_gpt,
        "gemini": ask_gemini,
        "grok": ask_grok,
        "claude": ask_claude,
    }

    results = {}

    with ThreadPoolExecutor(max_workers=4) as executor:
        future_map = {
            executor.submit(fn, prompt): name
            for name, fn in tasks.items()
        }

        for future in as_completed(future_map):
            name = future_map[future]
            try:
                results[name] = safe_text(future.result())
            except Exception as e:
                results[name] = {"error": str(e)}

    return results


# ---------------------------------------------------------
# Main API endpoint
# ---------------------------------------------------------
@app.get("/ask")
async def ask(q: str):
    if not q or q.strip() == "":
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Prompt tuning
    prompt = f"{tune_prompt(q)}\n\n{q}"

    # Run models
    answers = run_parallel(prompt)

    # Safe processing (prevents downstream crashes)
    clean_answers = {k: safe_text(v) for k, v in answers.items()}

    try:
        cons = consensus(clean_answers)
    except Exception as e:
        cons = f"Consensus error: {e}"

    try:
        contra = contradictions(clean_answers)
    except Exception as e:
        contra = f"Contradiction error: {e}"

    try:
        scores = weighted_scores(clean_answers)
    except Exception as e:
        scores = f"Scoring error: {e}"

    # Cost estimation (safe)
    costs = {
        k: estimate_cost(v) if isinstance(v, str) else 0
        for k, v in clean_answers.items()
    }

    result = {
        "query": q,
        "prompt_used": prompt,
        "answers": clean_answers,
        "consensus": cons,
        "contradictions": contra,
        "scores": scores,
        "costs": costs,
    }

    # Logging (never crash app if logging fails)
    try:
        save_log(result)
    except Exception:
        pass

    return result