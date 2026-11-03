"""Whose key a hosted engine spends: the signed-in user's own, one user at a time, never the operator's by default."""
import os

import pytest

import llm_credentials
import llm_provider
import pipeline_trace
import run_options

ISSUER = "https://clerk.example.test"
_SETTINGS = ("LLM_PROVIDER", "LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "CLAUDE_API_KEY", "OPENAI_BASE_URL",
             "LLM_MODEL", "LLM_MODEL_RED_TEST_GENERATION", "CLERK_ISSUER", "LLM_HOUSE_USERS")


@pytest.fixture(autouse=True)
def _clean(monkeypatch):
    for name in _SETTINGS:
        monkeypatch.delenv(name, raising=False)
    yield
    llm_credentials.reset()


def _user_key(provider="anthropic", user="user_a", api_key="user-secret-key-123"):
    return llm_credentials.Credential(user_id=user, provider=provider, api_key=api_key)


def test_without_login_the_settings_decide_as_before(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "operator-key")
    assert llm_provider.connection().api_key == "operator-key"


def test_a_hosted_engine_never_falls_back_to_the_operators_key(monkeypatch):
    """
    Given: a hosted engine that holds the operator's key
    When: a call runs for nobody, or for a user without a key of their own
    Then: it has no key, and its hint says where a user puts one
    """
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.setenv("GEMINI_API_KEY", "operator-key")
    assert llm_provider.connection().api_key == ""
    with llm_credentials.holding(llm_credentials.Credential(user_id="user_a")):
        connection = llm_provider.connection()
    assert connection.api_key == "" and "Studio" in connection.key_hint


def test_a_users_key_chooses_its_provider_and_ignores_operator_model_settings(monkeypatch):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_MODEL_RED_TEST_GENERATION", "gemini-only-model")
    with llm_credentials.holding(_user_key("anthropic")):
        connection = llm_provider.connection("red_test_generation")
        models = llm_provider.stage_models()
    assert connection.api_key == "user-secret-key-123" and connection.api == "anthropic"
    assert connection.model == llm_provider.PROVIDERS["anthropic"].model
    assert models == llm_provider.PROVIDERS["anthropic"].stage_models


def test_a_run_held_on_one_model_still_applies_to_a_users_key(monkeypatch):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    with llm_credentials.holding(_user_key("anthropic")), run_options.running_with(run_options.RunOptions(model="m")):
        assert llm_provider.connection().model == "m"


def test_a_house_user_runs_on_the_operators_settings(monkeypatch):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.setenv("GEMINI_API_KEY", "operator-key")
    with llm_credentials.holding(llm_credentials.Credential(user_id="owner", house=True)):
        assert llm_provider.connection().api_key == "operator-key"


def test_a_second_user_is_refused_while_one_users_work_runs(monkeypatch):
    """Worker threads of a run all read the one held key, so a second user's request must never replace it."""
    with llm_credentials.holding(_user_key(user="user_a")):
        with pytest.raises(llm_credentials.EngineBusy):
            with llm_credentials.holding(_user_key(user="user_b", api_key="another-secret-key")):
                pass
        with llm_credentials.holding(_user_key(user="user_a")):  # the same user's next request joins in
            pass
        assert llm_credentials.current().api_key == "user-secret-key-123"
    assert llm_credentials.current() is None


def test_the_same_users_requests_keep_the_hold_until_the_last_ends(monkeypatch):
    first = llm_credentials.acquire(_user_key())
    second = llm_credentials.acquire(_user_key())
    llm_credentials.release(second)
    assert llm_credentials.current() is first
    llm_credentials.release(first)
    assert llm_credentials.current() is None


def test_sealing_moves_every_secret_out_of_what_subprocesses_inherit(monkeypatch):
    """
    Given: a hosted engine with secrets in its environment
    When: the environment is sealed
    Then: a child process inherits none, while the engine still reads them
    """
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.setenv("GEMINI_API_KEY", "operator-key")
    monkeypatch.setenv("PROVABLE_KEY_SECRET", "master-secret-value")
    llm_credentials.seal_environment()
    assert "GEMINI_API_KEY" not in os.environ and "PROVABLE_KEY_SECRET" not in os.environ
    assert llm_credentials.setting("PROVABLE_KEY_SECRET") == "master-secret-value"
    with llm_credentials.holding(llm_credentials.Credential(user_id="owner", house=True)):
        assert llm_provider.connection().api_key == "operator-key"


def test_a_local_engine_keeps_its_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "operator-key")
    llm_credentials.seal_environment()
    assert os.environ["GEMINI_API_KEY"] == "operator-key"


def test_every_providers_key_setting_is_sealed_and_scrubbed():
    for provider in llm_provider.PROVIDERS.values():
        assert provider.key_env in llm_credentials.SECRET_SETTINGS


def test_traces_scrub_the_held_key_the_sealed_keys_and_the_claude_key(monkeypatch):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.setenv("CLAUDE_API_KEY", "claude-operator-key")
    assert "claude-operator-key" not in pipeline_trace._scrub("claude-operator-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-operator-key")
    llm_credentials.seal_environment()
    assert "gemini-operator-key" not in pipeline_trace._scrub("gemini-operator-key")
    with llm_credentials.holding(_user_key()):
        assert "user-secret-key-123" not in pipeline_trace._scrub("failed with user-secret-key-123")
