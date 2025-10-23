import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("⚠️ GROQ_API_KEY missing in .env file")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_groq(prompt, model="openai/gpt-oss-120b"):
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}\n{response.text if 'response' in locals() else ''}"
