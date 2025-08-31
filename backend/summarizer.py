# backend/summarizer.py
import os
from dotenv import load_dotenv
import cohere

load_dotenv()

# default model; aap COHERE_MODEL env me change kar sakte ho
MODEL_TEXT = os.getenv("COHERE_MODEL", "command-r-plus-08-2024")

# Cohere client
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY missing in .env")
co = cohere.Client(COHERE_API_KEY)

def _style(length: str) -> str:
    return {
        "short":  "3-5 bullets, crisp.",
        "medium": "6-9 bullets with a 2-line gist.",
        "long":   "10-15 bullets + short abstract.",
    }.get(length, "6-9 bullets with a 2-line gist.")

def summarize_text(text: str, length: str = "medium") -> str:
    prompt = (
        "Summarize the following document.\n"
        f"Style: {_style(length)}\n\n{text[:12000]}"
    )
    try:
        # simple single-turn chat
        resp = co.chat(model=MODEL_TEXT, message=prompt)
        return (resp.text or "").strip()
    except Exception as e:
        # bubble up as clean error
        raise RuntimeError(f"Cohere error: {e}")

def summarize_image(image_bytes: bytes, length: str = "medium") -> str:
    # Cohere ke paas abhi OpenAI-jaisa vision OCR summarization direct nahi hai.
    # Agar image support chahiye to Tesseract OCR + Cohere ka combo add karenge.
    raise RuntimeError("Image summarization not supported with Cohere yet.")