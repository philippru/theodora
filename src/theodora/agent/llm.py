"""Provider-agnostic LLM access via LiteLLM (optional `[agent]` extra).

One interface for Claude, OpenAI/ChatGPT, Gemini, AWS Bedrock, Azure/Microsoft, and local
models (Ollama, …). Pick the model with `--model` or `$THEODORA_LLM_MODEL`; provider API keys
are read from the standard env vars (ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY /
AWS_* / AZURE_* / OLLAMA_HOST). A `Proposer` is just `Callable[[str], str]`, so tests inject a
fake one — no network or keys needed.
"""
from __future__ import annotations

import os
from collections.abc import Callable

Proposer = Callable[[str], str]

# Example model ids per provider (LiteLLM naming) — for `--model` / docs.
PROVIDER_EXAMPLES: dict[str, str] = {
    "claude": "anthropic/claude-sonnet-4-6",
    "openai": "openai/gpt-4o-mini",
    "gemini": "gemini/gemini-2.0-flash",
    "bedrock": "bedrock/anthropic.claude-3-5-sonnet-20241022-v2:0",
    "azure": "azure/<your-deployment>",
    "local": "ollama/llama3.1",
}

DEFAULT_MODEL = os.environ.get("THEODORA_LLM_MODEL", "anthropic/claude-sonnet-4-6")

_SYSTEM = (
    "You correct a single cell value in a DORA Register-of-Information report. "
    "Reply with ONLY the corrected value — no quotes, no explanation."
)


def available() -> bool:
    try:
        import litellm  # noqa: F401
        return True
    except ImportError:
        return False


_EXTRACT_SYSTEM = (
    "You extract structured values from a contract for a DORA Register-of-Information template. "
    "Reply with ONLY a JSON object mapping field keys (cXXXX) to values; omit unknown fields."
)


def extractor(model: str | None = None) -> Proposer:
    """Return a Proposer tuned for JSON extraction (larger output, extraction system prompt)."""
    import litellm

    chosen = model or DEFAULT_MODEL

    def propose(prompt: str) -> str:
        resp = litellm.completion(
            model=chosen,
            messages=[{"role": "system", "content": _EXTRACT_SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=800,
        )
        return (resp.choices[0].message.content or "").strip()

    return propose


def litellm_proposer(model: str | None = None) -> Proposer:
    """Return a Proposer backed by LiteLLM for the given (or default) model."""
    import litellm

    chosen = model or DEFAULT_MODEL

    def propose(prompt: str) -> str:
        resp = litellm.completion(
            model=chosen,
            messages=[{"role": "system", "content": _SYSTEM}, {"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=64,
        )
        return (resp.choices[0].message.content or "").strip()

    return propose
