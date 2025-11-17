import os, json
from sqlalchemy import text
from db import engine
import google.generativeai as genai

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def embed(t):
    return genai.embed_content(
        model=os.environ["GEMINI_EMBED_MODEL"],
        content=t
    )["embedding"]

def lambda_handler(event=None, ctx=None):
    docs = [
        ("How to reset VPN?", {"category": "it"}),
        ("Leave policy description...", {"category": "hr"}),
        ("Password reset steps...", {"category": "it"}),
    ]

    with engine.begin() as conn:
        for text_value, meta in docs:
            conn.execute(
                text("INSERT INTO documents (text, embedding, metadata) VALUES (:t, :e, :m)"),
                {
                    "t": text_value,
                    "e": embed(text_value),
                    "m": json.dumps(meta)
                }
            )
    return {"status": "ok"}
