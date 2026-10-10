"""Unit tests for which provider the LLM calls go to (backend/llm_provider.py)."""

import pytest

import agent_orchestrator
import llm_provider

_REAL_CALL_GEMINI = agent_orchestrator.call_gemini  # conftest replaces the attribute with an offline double

_SETTINGS = ("LLM_PROVIDER", "LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "OPENAI_BASE_URL", "LLM_MODEL",
             "LLM_MODEL_RED_TEST_GENERATION", "LLM_MODEL_PROMPT_EXPANSION")


@pytest.fixture(autouse=True)
def no_llm_settings(monkeypatch):
    for name in _SETTINGS:
        monkeypatch.delenv(name, raising=False)


def test_a_named_provider_brings_its_own_endpoint_key_and_model(monkeypatch):
    """Verify one setting switches the endpoint, the key and the model together.

    id: TST-PROV-001
    Given: Keys for two providers, and LLM_PROVIDER naming one of them
    When: The connection is resolved, then the other provider is named
    Then: Each time the endpoint, the key and the model are that provider's
    """
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    for name in ("openai", "gemini"):
        monkeypatch.setenv("LLM_PROVIDER", name)
        provider, connection = llm_provider.PROVIDERS[name], llm_provider.connection()
        assert (connection.base_url, connection.model) == (provider.base_url, provider.model)
        assert connection.api_key == f"{name}-key"


def test_a_named_provider_is_not_mixed_with_the_single_settings(monkeypatch):
    """Verify a leftover endpoint or model of another provider cannot leak into the named one.

    id: TST-PROV-002
    Given: LLM_PROVIDER naming a provider, with OPENAI_BASE_URL, LLM_API_KEY and LLM_MODEL left from another setup
    When: The connection is resolved
    Then: Only the stage override is honoured; the rest is the named provider's
    """
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    monkeypatch.setenv("LLM_API_KEY", "other-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://other.example/v1")
    monkeypatch.setenv("LLM_MODEL", "other-model")
    monkeypatch.setenv("LLM_MODEL_RED_TEST_GENERATION", "test-writer-model")
    connection = llm_provider.connection()
    assert connection.api_key == "openai-key" and connection.base_url == llm_provider.PROVIDERS["openai"].base_url
    assert connection.model == llm_provider.PROVIDERS["openai"].model
    assert llm_provider.connection("red_test_generation").model == "test-writer-model"


def test_without_a_named_provider_the_single_settings_decide(monkeypatch):
    """Verify a setup that names no provider keeps working as before.

    id: TST-PROV-003
    Given: No LLM_PROVIDER; first only a Gemini key, then a custom endpoint, key and model
    When: The connection is resolved
    Then: It is the Gemini default, then the custom one
    """
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    default = llm_provider.connection()
    assert (default.base_url, default.model, default.api_key) == (
        llm_provider.PROVIDERS["gemini"].base_url, llm_provider.PROVIDERS["gemini"].model, "gemini-key")
    monkeypatch.setenv("LLM_API_KEY", "custom-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://custom.example/v1")
    monkeypatch.setenv("LLM_MODEL", "custom-model")
    custom = llm_provider.connection()
    assert (custom.base_url, custom.model, custom.api_key) == ("https://custom.example/v1", "custom-model", "custom-key")


def test_a_call_sends_a_temperature_only_to_a_provider_that_accepts_one(monkeypatch):
    """Verify a provider whose models run at a fixed temperature is not sent one it would reject.

    id: TST-PROV-005
    Given: A recording provider client, with LLM_PROVIDER naming first a provider that accepts a temperature, then one
        that does not, then no provider at all
    When: An LLM call is made each time
    Then: The request carries a temperature the first and last time, and none the second
    """
    sent = []

    class Completions:
        def create(self, **kwargs):
            sent.append(kwargs)
            raise RuntimeError("stop here")

    class Client:
        def __init__(self, **_):
            self.chat = type("Chat", (), {"completions": Completions()})()

    monkeypatch.setattr(agent_orchestrator, "OpenAI", Client)
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    for name in ("gemini", "openai", None):
        if name:
            monkeypatch.setenv("LLM_PROVIDER", name)
        else:
            monkeypatch.delenv("LLM_PROVIDER")
        _REAL_CALL_GEMINI("p", stage="s")
    assert ["temperature" in request for request in sent] == [True, False, True]
    assert llm_provider.connection().accepts_temperature


def test_an_unknown_provider_fails_loudly_and_a_missing_key_is_named(monkeypatch):
    """Verify a typo in the provider name is not answered by silently using another provider.

    id: TST-PROV-004
    Given: LLM_PROVIDER naming a provider that does not exist, then a real one whose key is not set
    When: The connection is resolved
    Then: The first raises naming the known providers; the second has no key and names the setting to fill
    """
    monkeypatch.setenv("LLM_PROVIDER", "nobody")
    with pytest.raises(ValueError, match="gemini"):
        llm_provider.connection()
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    connection = llm_provider.connection()
    assert connection.api_key == "" and "OPENAI_API_KEY" in connection.key_hint


def test_a_provider_may_give_one_stage_a_model_of_its_own(monkeypatch):
    """Verify the pitch expansion runs on the provider's steadier model unless a setting says otherwise.

    id: TST-PROV-006
    Given: The anthropic provider, whose expansion was measured on three models (reference/expansion-models)
    When: The connection of the expansion, of another stage and of the comparison provider is resolved
    Then: The expansion uses the middle model, every other stage the provider's own, a stage setting still wins,
          and the provider a build is compared against keeps its one model for every stage
    """
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    assert llm_provider.connection("prompt_expansion").model == "claude-sonnet-5-5"
    assert llm_provider.connection("ux_planning").model == "claude-haiku-5-5"
    assert llm_provider.connection().model == "claude-haiku-5-5"

    monkeypatch.setenv("LLM_MODEL_PROMPT_EXPANSION", "claude-haiku-5-5")
    assert llm_provider.connection("prompt_expansion").model == "claude-haiku-5-5"

    monkeypatch.delenv("LLM_MODEL_PROMPT_EXPANSION")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic-opus")
    assert llm_provider.connection("prompt_expansion").model == "claude-opus-5-5"
