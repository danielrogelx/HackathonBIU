import os
import httpx
from dotenv import load_dotenv

load_dotenv()

MODEL = "anthropic/claude-sonnet-4-5"
BASE_URL = "https://openrouter.ai/api/v1"


def call_openrouter(messages: list[dict], system: str) -> str:
    """Call OpenRouter and return the assistant message text."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set in .env")

    resp = httpx.post(
        f"{BASE_URL}/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://github.com/danielrogelx/HackathonBIU",
            "X-Title": "Court Practice Simulator",
        },
        json={
            "model": MODEL,
            "messages": [{"role": "system", "content": system}] + messages,
        },
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]
