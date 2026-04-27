from concurrent.futures import ThreadPoolExecutor, as_completed
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from agents import ask_gemini, ask_huggingface, ask_ollama
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
        "message": "Multi-AI Agent API (free-tier mode)"
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
def normalize_provider_result(value):
    if isinstance(value, dict):
        if "error" in value:
            return {"answer": "", "error": str(value["error"])}
        return {"answer": str(value), "error": None}
    if value is None:
        return {"answer": "", "error": "Empty response"}
    return {"answer": str(value), "error": None}


# ---------------------------------------------------------
# Parallel execution helper
# ---------------------------------------------------------
def run_parallel(prompt: str):
    tasks = {
        "gemini": ask_gemini,
        "huggingface": ask_huggingface,
        "ollama": ask_ollama,
    }

    results = {}

    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        future_map = {
            executor.submit(fn, prompt): name
            for name, fn in tasks.items()
        }

        for future in as_completed(future_map):
            name = future_map[future]
            try:
                results[name] = normalize_provider_result(future.result())
            except Exception as e:
                results[name] = {"answer": "", "error": str(e)}

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
    provider_results = run_parallel(prompt)

    clean_answers = {
        name: result["answer"]
        for name, result in provider_results.items()
        if result["answer"]
    }
    provider_errors = {
        name: result["error"]
        for name, result in provider_results.items()
        if result["error"]
    }

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
        k: estimate_cost(v)
        for k, v in clean_answers.items()
    }

    result = {
        "query": q,
        "prompt_used": prompt,
        "answers": clean_answers,
        "errors": provider_errors,
        "providers": provider_results,
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
