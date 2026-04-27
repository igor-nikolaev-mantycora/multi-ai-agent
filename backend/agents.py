import os

import requests
from dotenv import load_dotenv
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

load_dotenv()

GEMINI = os.getenv("GEMINI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")


def safe(f):
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )(f)


def require_api_key(name, value):
    if value:
        return value
    raise RuntimeError(f"{name} is not configured")


@safe
def ask_gemini(prompt):
    api_key = require_api_key("GEMINI_API_KEY", GEMINI)

    try:
        import google.genai as genai

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
    except ModuleNotFoundError:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(prompt)
        return response.text


@safe
def ask_huggingface(prompt):
    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="hf-inference",
        api_key=require_api_key("HF_TOKEN", HF_TOKEN),
    )

    completion = client.chat.completions.create(
        model=HF_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.2,
    )

    return completion.choices[0].message.content


@safe
def ask_ollama(prompt):
    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    answer = data.get("response")
    if not answer:
        raise RuntimeError(f"Ollama response missing text: {data}")
    return answer
