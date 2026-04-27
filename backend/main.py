from fastapi import FastAPI
from concurrent.futures import ThreadPoolExecutor
from agents import ask_gpt, ask_gemini, ask_grok, ask_claude
from logic import consensus, contradictions, weighted_scores
from prompts import tune_prompt
from utils import estimate_cost, save_log

app = FastAPI()

def run_parallel(prompt):
    with ThreadPoolExecutor() as ex:
        futures = {
            "gpt": ex.submit(ask_gpt, prompt),
            "gemini": ex.submit(ask_gemini, prompt),
            "grok": ex.submit(ask_grok, prompt),
            "claude": ex.submit(ask_claude, prompt),
        }
    return {k: f.result() for k, f in futures.items()}


@app.get("/ask")
def ask(q: str):

    prompt = f"{tune_prompt(q)}\n\n{q}"

    answers = run_parallel(prompt)

    result = {
        "answers": answers,
        "consensus": consensus(answers),
        "contradictions": contradictions(answers),
        "scores": weighted_scores(answers),
        "costs": {k: estimate_cost(v) for k,v in answers.items()}
    }

    save_log(result)

    return result