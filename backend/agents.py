import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

OPENAI = os.getenv("OPENAI_API_KEY")
GEMINI = os.getenv("GEMINI_API_KEY")
GROK = os.getenv("GROK_API_KEY")
CLAUDE = os.getenv("CLAUDE_API_KEY")

def safe(f):
    return retry(stop=stop_after_attempt(3), wait=wait_fixed(2))(f)

@safe
def ask_gpt(prompt):
    from openai import OpenAI
    c = OpenAI(api_key=OPENAI)
    r = c.chat.completions.create(
        model="gpt-5",
        messages=[{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content

@safe
def ask_gemini(prompt):
    import google.generativeai as genai
    genai.configure(api_key=GEMINI)
    return genai.GenerativeModel("gemini-pro").generate_content(prompt).text

@safe
def ask_grok(prompt):
    import requests
    r = requests.post(
        "https://api.x.ai/v1/chat/completions",
        headers={"Authorization":f"Bearer {GROK}"},
        json={"model":"grok-1","messages":[{"role":"user","content":prompt}]}
    )
    return r.json()["choices"][0]["message"]["content"]

@safe
def ask_claude(prompt):
    import anthropic
    c = anthropic.Anthropic(api_key=CLAUDE)
    r = c.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1000,
        messages=[{"role":"user","content":prompt}]
    )
    return r.content[0].text