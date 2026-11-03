"""Which provider the LLM calls go to: an endpoint, the key for it and the model, switched together.

LLM_PROVIDER names one of PROVIDERS, and that provider then supplies the endpoint, the key (from its own setting, so
the keys of several providers can sit side by side) and the default model. A provider may give a stage a model of its own (stage_models); LLM_MODEL_<STAGE> moves any stage to
another model of the same provider. Without LLM_PROVIDER the single settings decide, as before: LLM_API_KEY /
OPENAI_API_KEY / GEMINI_API_KEY, OPENAI_BASE_URL and LLM_MODEL, defaulting to Gemini. On a hosted engine a user's own
key (llm_credentials.py) decides instead, and the operator's key is never a fallback.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

import llm_credentials


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
                                        "product_contract": "claude-sonnet-5-5",
                                        # A change is planned against that contract and written in its form
                                        # (ADR-014); not yet measured on the small model.
                                        "change_ticket": "claude-sonnet-5-5",
                                        # Where the fault of a red rule lies decides what a fix may change. On one
                                        # recorded case the middle model named the rule that contradicts the plan in
                                        # 2 of 2 answers of 5 to 7 s; the small one in 3 of 4, of 10 to 15 s.
                                        "rule_diagnosis": "claude-sonnet-5-5",
                                        # The rule deck is checked against the plan it was written with
                                        # (onboarding/spec_review.py). On a contract with a rule that contradicts
                                        # its action the middle model named it in 2 of 2 answers of 8 s; the small
                                        # one missed it in 15 s. It runs beside the builders, so it adds no time.
                                        "spec_consistency_review": "claude-sonnet-5-5",
                                        # The rules that review names are written again by the writer of the plan
                                        # (onboarding/plan_rework.py); not measured on the small model.
                                        "plan_rework": "claude-sonnet-5-5"},
                          # The small model thinks by default. Writing the page from the contract and the plan, that
                          # was four fifths of the answer's tokens and of its time (67 s against 12 s, ADR-011). The
                          # first tests of a class are transcribed from the contract's rules, which state every value
                          # (onboarding/first_tests.py): 8 s without thinking, each test faithful to its rule. The
                          # code writer and a test writer asked again keep it: without, they left rules unfulfilled.
                          unthinking_stages=("presentation_projection_synthesis", "first_tests")),
    # The larger model of the same family, on the same key: what a build is compared against.
    "anthropic-opus": Provider("https://api.anthropic.com/v1/", "claude-opus-5-5", "CLAUDE_API_KEY",
                               accepts_temperature=False, api="anthropic"),
    # The middle model on every stage: the same build at the middle model's quality and price.
    "anthropic-sonnet": Provider("https://api.anthropic.com/v1/", "claude-sonnet-5-5", "CLAUDE_API_KEY",
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


def _users_own() -> Optional[llm_credentials.Credential]:
    """The held user's own key, which brings its provider along and leaves the operator's model settings out."""
    held = llm_credentials.current()
    return held if held and held.api_key else None


def _operators_settings_apply() -> bool:
    held = llm_credentials.current()
    return not llm_credentials.enforced() or bool(held and held.house)


def _provider_name() -> str:
    own = _users_own()
    return own.provider if own else (os.environ.get("LLM_PROVIDER") or "").strip().lower()


def stage_models() -> Dict[str, str]:
    """The stages that run on another model than the default one, by the provider or a setting, with that model."""
    name = _provider_name()
    models = dict(PROVIDERS[name].stage_models) if name in PROVIDERS else {}
    if _users_own():
        return models
    prefix = "LLM_MODEL_"
    models.update({key[len(prefix):].lower(): value for key, value in os.environ.items()
                   if key.startswith(prefix) and value})
    return models


def connection(stage: str = "general") -> Connection:
    """The endpoint, key and model the given stage's call uses."""
    import run_options
    own = _users_own()
    # A run held on one model asks it of every stage, as a stage moved by a setting is (run_options.py)
    stage_model = run_options.current().model or (None if own else os.environ.get(f"LLM_MODEL_{stage.upper()}"))
    operators = _operators_settings_apply()
    bring_your_own = "add your own key in the Studio"
    name = _provider_name()
    if name:
        if name not in PROVIDERS:
            raise ValueError(f"LLM_PROVIDER={name!r} is not a known provider (known: {', '.join(sorted(PROVIDERS))}).")
        provider = PROVIDERS[name]
        model = stage_model or provider.stage_models.get(stage) or provider.model
        # A stage moved to another model by a setting was not measured there, so that model is left as it is.
        thinking = bool(stage_model) or stage not in provider.unthinking_stages
        api_key = own.api_key if own else llm_credentials.setting(provider.key_env) if operators else ""
        return Connection(provider.base_url, api_key, model, f"set {provider.key_env}" if operators else bring_your_own,
                          provider.accepts_temperature, provider.api, thinking)
    default = PROVIDERS["gemini"]
    api_key = (llm_credentials.setting("LLM_API_KEY") or llm_credentials.setting("OPENAI_API_KEY")
               or llm_credentials.setting("GEMINI_API_KEY")) if operators else ""
    return Connection(os.environ.get("OPENAI_BASE_URL") or default.base_url, api_key,
                      stage_model or os.environ.get("LLM_MODEL") or default.model,
                      "set GEMINI_API_KEY, LLM_API_KEY or OPENAI_API_KEY" if operators else bring_your_own)
