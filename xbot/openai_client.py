import os
from openai import OpenAI

# DÜZELTME: Geçerli bir model ismi girildi.
MODEL_NAME = "gpt-4o" 


def build_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing.")
    return OpenAI(api_key=api_key)


def generate_text(client: OpenAI, prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=200, # Biraz artırıldı, cümle yarıda kalmasın.
        temperature=0.7, # Yaratıcılık için eklenebilir (isteğe bağlı)
    )

    content = resp.choices[0].message.content
    if not content:
        print("[WARN] LLM returned no content.")
        return ""

    text = content.strip()
    if not text:
        print("[WARN] LLM returned empty text after stripping.")
        return ""

    if len(text) > 280: # Twitter limiti 280
        text = text[:280]

    return text