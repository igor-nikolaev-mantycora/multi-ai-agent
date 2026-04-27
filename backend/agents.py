import os
import requests
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

load_dotenv()

OPENAI = os.getenv("OPENAI_API_KEY")
GEMINI = os.getenv("GEMINI_API_KEY")
GROK = os.getenv("GROK_API_KEY")
CLAUDE = os.getenv("CLAUDE_API_KEY")


# ---------------------------------------------------------
# Retry wrapper for all model calls
# ---------------------------------------------------------
def safe(f):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception)
    )(f)


# ---------------------------------------------------------
# GPT‑5 (OpenAI Responses API)
# ---------------------------------------------------------
@safe
def ask_gpt(prompt):
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI)

    r = client.responses.create(
        model="gpt-5",
        input=prompt,
        max_output_tokens=800
    )

    return r.output_text


# ---------------------------------------------------------
# Gemini 2.0 (google.genai — NEW PACKAGE)
# ---------------------------------------------------------
@safe
def ask_gemini(prompt):
    import google.genai as genai

    client = genai.Client(api_key=GEMINI)

    response = client.models.generate_content(
        model="gemini-2.0-pro",
        contents=prompt
    )

    return response.text


# ---------------------------------------------------------
# Grok‑2 (xAI)
# ---------------------------------------------------------
@safe
def ask_grok(prompt):
    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {GROK}"},
        json={
            "model": "grok-2-latest",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800
        },
        timeout=30
    )

    data = r.json()

    return data["choices"][0]["message"]["content"]


# ---------------------------------------------------------
# Claude 3.5 Sonnet (Anthropic)
# ---------------------------------------------------------
@safe
def ask_claude(prompt):
    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE)

    r = client.messages.create(
        model="claude-3.5-sonnet-latest",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}]
    )

    return r.content[0].text
