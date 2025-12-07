import os
from openai import OpenAI

MODEL_NAME = "gpt-4.1"


def build_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing.")
    return OpenAI(api_key=api_key)


def generate_text(client: OpenAI, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=160,
        # GPT-5 mini için temperature göndermiyoruz
    )

    content = resp.choices[0].message.content
    if not content:
        print("[WARN] LLM returned no content.")
        return ""

    text = content.strip()
    if not text:
        print("[WARN] LLM returned empty text after stripping.")
        return ""

    if len(text) > 260:
        text = text[:260]

    return text
