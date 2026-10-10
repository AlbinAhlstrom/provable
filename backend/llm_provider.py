"""Which provider the LLM calls go to: an endpoint, the key for it and the model, switched together.

LLM_PROVIDER names one of PROVIDERS, and that provider then supplies the endpoint, the key (from its own setting, so
the keys of several providers can sit side by side) and the default model. LLM_MODEL_<STAGE> still moves one stage to
another model of the same provider. Without LLM_PROVIDER the single settings decide, as before: LLM_API_KEY /
OPENAI_API_KEY / GEMINI_API_KEY, OPENAI_BASE_URL and LLM_MODEL, defaulting to Gemini.
"""

import os
from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Provider:
    base_url: str
    model: str
    key_env: str
    accepts_temperature: bool = True  # False when its models run only at their own fixed temperature
    api: str = "openai"  # which API a call speaks: "openai" (chat completions) or "anthropic" (llm_anthropic.py)


PROVIDERS: Dict[str, Provider] = {
    "gemini": Provider("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.8-flash", "GEMINI_API_KEY"),
    "openai": Provider("https://api.openai.com/v1", "gpt-6-luna", "OPENAI_API_KEY", accepts_temperature=False),
    # base_url is its OpenAI-compatible endpoint, for the callers that only speak that API.
    "anthropic": Provider("https://api.anthropic.com/v1/", "claude-haiku-5-5", "CLAUDE_API_KEY",
                          accepts_temperature=False, api="anthropic"),
    # The larger model of the same family, on the same key: what a build is compared against.
    "anthropic-opus": Provider("https://api.anthropic.com/v1/", "claude-opus-5-5", "CLAUDE_API_KEY",
                               accepts_temperature=False, api="anthropic"),
}


@dataclass(frozen=True)
class Connection:
    base_url: str
    api_key: str
    model: str
    key_hint: str  # which setting to fill when api_key is empty
    accepts_temperature: bool = True
    api: str = "openai"


def connection(stage: str = "general") -> Connection:
    """The endpoint, key and model the given stage's call uses."""
    stage_model = os.environ.get(f"LLM_MODEL_{stage.upper()}")
    name = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if name:
        if name not in PROVIDERS:
            raise ValueError(f"LLM_PROVIDER={name!r} is not a known provider (known: {', '.join(sorted(PROVIDERS))}).")
        provider = PROVIDERS[name]
        return Connection(provider.base_url, os.environ.get(provider.key_env) or "", stage_model or provider.model,
                          f"set {provider.key_env}", provider.accepts_temperature, provider.api)
    default = PROVIDERS["gemini"]
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    return Connection(os.environ.get("OPENAI_BASE_URL") or default.base_url, api_key or "",
                      stage_model or os.environ.get("LLM_MODEL") or default.model,
                      "set GEMINI_API_KEY, LLM_API_KEY or OPENAI_API_KEY")
