from __future__ import annotations

import os
GROQ_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_MODEL   = "llama-3.1-8b-instant"

def ask_llm(
    prompt: str,
    *,
    system: str = "",
    history: list[dict] | None = None,
    max_tokens: int = 1500,
    model: str | None = None,
) -> str:
    history = history or []
    model   = model or GROQ_MODEL
    return _call_groq(prompt, system, history, max_tokens, model)


def _call_groq(prompt, system, history, max_tokens, model):
    from openai import OpenAI

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages += history
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content