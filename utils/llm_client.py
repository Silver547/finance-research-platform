"""
Thin, provider-agnostic LLM client.

Supports:
  - "gemini"     -> Google AI Studio free tier (google-generativeai)
  - "openrouter" -> OpenRouter free models (plain HTTPS, OpenAI-style schema)
  - "ollama"     -> Local models via Ollama's REST API (fully offline)

Pick the provider in .env (LLM_PROVIDER). All pipelines/agents call
`call_llm(prompt)` and don't need to know which backend is behind it.
"""
import json
import requests
from config.settings import settings


def _call_gemini(prompt: str, model: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=settings.GOOGLE_AI_STUDIO_KEY)
    gen_model = genai.GenerativeModel(model or "gemini-1.5-flash")
    response = gen_model.generate_content(prompt)
    return response.text


def _call_openrouter(prompt: str, model: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}"}
    payload = {
        "model": model or "qwen/qwen-2.5-7b-instruct:free",
        "messages": [{"role": "user", "content": prompt}],
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_ollama(prompt: str, model: str) -> str:
    url = f"{settings.OLLAMA_BASE_URL}/api/generate"
    payload = {"model": model or "llama3.1:8b", "prompt": prompt, "stream": False}
    resp = requests.post(url, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]


def call_llm(prompt: str, model: str | None = None, provider: str | None = None) -> str:
    """
    Send `prompt` to the configured LLM provider and return the raw text response.
    Raises a clear error if no API key is configured for the chosen provider,
    rather than failing silently.
    """
    provider = provider or settings.LLM_PROVIDER
    model = model or settings.LLM_MODEL

    if provider == "gemini":
        if not settings.GOOGLE_AI_STUDIO_KEY:
            raise RuntimeError(
                "GOOGLE_AI_STUDIO_KEY is not set. Get a free key at "
                "https://aistudio.google.com/ and add it to your .env file."
            )
        return _call_gemini(prompt, model)

    if provider == "openrouter":
        if not settings.OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Get a free key at "
                "https://openrouter.ai/ and add it to your .env file."
            )
        return _call_openrouter(prompt, model)

    if provider == "ollama":
        return _call_ollama(prompt, model)

    raise ValueError(f"Unknown LLM_PROVIDER '{provider}'. Use gemini | openrouter | ollama.")


def call_llm_json(prompt: str, model: str | None = None, provider: str | None = None) -> dict:
    """
    Convenience wrapper for prompts that ask the model to return JSON.
    Strips markdown code fences if the model wraps its output in them.
    """
    raw = call_llm(prompt, model=model, provider=provider)
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    return json.loads(cleaned.strip())
