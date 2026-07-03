import os
import httpx
from app.config import settings


async def get_embedding(text: str) -> list:
    api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return [0.0] * 768

    url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={api_key}"
    payload = {
        "model": "models/text-embedding-004",
        "content": {"parts": [{"text": text[:2048]}]},
    }
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, timeout=15.0)
            if r.status_code == 200:
                return r.json()["embedding"]["values"]
    except Exception as e:
        print(f"Embedding error: {e}")
    return [0.0] * 768
