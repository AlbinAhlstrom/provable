"""Which provider the LLM calls go to: an endpoint, the key for it and the model, switched together.

LLM_PROVIDER names one of PROVIDERS, and that provider then supplies the endpoint, the key (from its own setting, so
the keys of several providers can sit side by side) and the default model. A provider may give a stage a model of its own (stage_models); LLM_MODEL_<STAGE> moves any stage to
another model of the same provider. Without LLM_PROVIDER the single settings decide, as before: LLM_API_KEY /
OPENAI_API_KEY / GEMINI_API_KEY, OPENAI_BASE_URL and LLM_MODEL, defaulting to Gemini.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class Provider:
    base_url: str
    model: str
    key_env: str
    accepts_temperature: bool = True  # False when its models run only at their own fixed temperature
    api: str = "openai"  # which API a call speaks: "openai" (chat completions) or "anthropic" (llm_anthropic.py)
    stage_models: Dict[str, str] = field(default_factory=dict)  # a stage that runs on another model than `model`
    unthinking_stages: Tuple[str, ...] = ()  # stages whose model answers without its hidden thinking


PROVIDERS: Dict[str, Provider] = {
    "gemini": Provider("https://generativelanguage.googleapis.com/v1beta/openai/", "gemini-3.8-flash", "GEMINI_API_KEY"),
    "openai": Provider("https://api.openai.com/v1", "gpt-6-luna", "OPENAI_API_KEY", accepts_temperature=False),
    # base_url is its OpenAI-compatible endpoint, for the callers that only speak that API.
    # The expansion is one call that every later stage builds on: measured alone, the middle model wrote the
    # steadiest specification and added nothing the product never had (reference/expansion-models).
    "anthropic": Provider("https://api.anthropic.com/v1/", "claude-haiku-5-5", "CLAUDE_API_KEY",
                          accepts_temperature=False, api="anthropic",
                          stage_models={"prompt_expansion": "claude-sonnet-5-5",
                                        # The contract every later stage is derived from: measured alone, the middle
                                        # model answered in a third of the small one's time (ADR-011).
                                        "product_contract": "claude-sonnet-5-5"},
                          # The small model thinks by default. Writing the page from the contract and the plan, that
                          # was four fifths of the answer's tokens and of its time (67 s against 12 s, ADR-011). The
                          # first tests of a class are transcribed from the contract's rules, which state every value
                          # (onboarding/first_tests.py): 8 s without thinking, each test faithful to its rule. The
                          # code writer and a test writer asked again keep it: without, they left rules unfulfilled.
                          unthinking_stages=("presentation_projection_synthesis", "first_tests")),
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
    thinking: bool = True  # False: the call asks the model to answer without its hidden thinking


def connection(stage: str = "general") -> Connection:
    """The endpoint, key and model the given stage's call uses."""
    stage_model = os.environ.get(f"LLM_MODEL_{stage.upper()}")
    name = (os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if name:
        if name not in PROVIDERS:
            raise ValueError(f"LLM_PROVIDER={name!r} is not a known provider (known: {', '.join(sorted(PROVIDERS))}).")
        provider = PROVIDERS[name]
        model = stage_model or provider.stage_models.get(stage) or provider.model
        # A stage moved to another model by a setting was not measured there, so that model is left as it is.
        thinking = bool(stage_model) or stage not in provider.unthinking_stages
        return Connection(provider.base_url, os.environ.get(provider.key_env) or "", model,
                          f"set {provider.key_env}", provider.accepts_temperature, provider.api, thinking)
    default = PROVIDERS["gemini"]
    api_key = os.environ.get("LLM_API_KEY") or os.environ.get("OPENAI_API_KEY") or os.environ.get("GEMINI_API_KEY")
    return Connection(os.environ.get("OPENAI_BASE_URL") or default.base_url, api_key or "",
                      stage_model or os.environ.get("LLM_MODEL") or default.model,
                      "set GEMINI_API_KEY, LLM_API_KEY or OPENAI_API_KEY")
