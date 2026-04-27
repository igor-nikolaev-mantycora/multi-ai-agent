from fastapi import FastAPI
from logic import consensus_vote, detect_contradictions
from prompts import tune_prompt
from agents import ask_gpt, ask_gemini, ask_grok, ask_claude
from concurrent.futures import ThreadPoolExecutor

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

    tuned = tune_prompt(q)
    prompt = f"{tuned}\n\nQuestion:\n{q}"

    answers = run_parallel(prompt)

    consensus = consensus_vote(answers)
    contradictions = detect_contradictions(answers)

    return {
        "answers": answers,
        "consensus": consensus,
        "contradictions": contradictions
    }