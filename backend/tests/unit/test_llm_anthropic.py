"""Unit tests for calls to a provider that is reached through Anthropic's own API (backend/llm_anthropic.py)."""

import base64
from types import SimpleNamespace

import pytest

import agent_orchestrator
import llm_anthropic
import llm_provider

_REAL_CALL_GEMINI = agent_orchestrator.call_gemini  # conftest replaces the attribute with an offline double

_SETTINGS = ("LLM_PROVIDER", "LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "CLAUDE_API_KEY", "OPENAI_BASE_URL",
             "LLM_MODEL", "LLM_REASONING_EFFORT")


@pytest.fixture(autouse=True)
def no_llm_settings(monkeypatch):
    for name in _SETTINGS:
        monkeypatch.delenv(name, raising=False)


class _FakeAnthropic:
    """Records how the client was built and what one request carried, and answers with fixed blocks."""
    built, sent = [], []
    answer = None

    def __init__(self, **kwargs):
        type(self).built.append(kwargs)
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        type(self).sent.append(kwargs)
        if isinstance(self.answer, Exception):
            raise self.answer
        return self.answer


@pytest.fixture
def anthropic_client(monkeypatch):
    _FakeAnthropic.built, _FakeAnthropic.sent = [], []
    _FakeAnthropic.answer = SimpleNamespace(
        content=[SimpleNamespace(type="thinking", thinking="hidden"), SimpleNamespace(type="text", text="the answer")],
        stop_reason="end_turn",
        usage=SimpleNamespace(input_tokens=100, output_tokens=40, cache_read_input_tokens=20,
                              cache_creation_input_tokens=0))
    monkeypatch.setattr(llm_anthropic, "Anthropic", _FakeAnthropic)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("CLAUDE_API_KEY", "claude-key")
    return _FakeAnthropic


def test_the_anthropic_provider_brings_its_own_key_model_and_api(monkeypatch):
    """Verify naming the provider switches the key, the model and which API the call speaks.

    id: TST-ANTH-001
    Given: Keys for two providers, and LLM_PROVIDER naming anthropic
    When: The connection is resolved
    Then: The key is CLAUDE_API_KEY's, the model is the provider's, and the call goes through Anthropic's own API,
          while the other providers stay on the OpenAI-compatible one
    """
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("CLAUDE_API_KEY", "claude-key")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    connection = llm_provider.connection()
    assert (connection.api_key, connection.model) == ("claude-key", llm_provider.PROVIDERS["anthropic"].model)
    assert connection.api == "anthropic" and not connection.accepts_temperature
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    assert llm_provider.connection().api == "openai"
    monkeypatch.delenv("LLM_PROVIDER")
    assert llm_provider.connection().api == "openai"


def test_the_larger_anthropic_model_is_a_provider_of_its_own_with_the_same_key(monkeypatch):
    """Verify the larger model of the family is chosen by name, with the key and the API of the smaller one.

    id: TST-ANTH-007
    Given: CLAUDE_API_KEY, and LLM_PROVIDER naming anthropic-opus
    When: The connection is resolved
    Then: The model is the larger one and differs from the anthropic provider's, the key and the API are the same,
          and the model has a price
    """
    import llm_cost
    monkeypatch.setenv("CLAUDE_API_KEY", "claude-key")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic-opus")
    connection = llm_provider.connection()
    assert connection.model != llm_provider.PROVIDERS["anthropic"].model
    assert (connection.api_key, connection.api, connection.accepts_temperature) == ("claude-key", "anthropic", False)
    assert llm_cost.price_for(connection.model).output > llm_cost.price_for(llm_provider.PROVIDERS["anthropic"].model).output


def test_a_call_carries_the_effort_and_returns_the_text_and_its_tokens(anthropic_client, monkeypatch):
    """Verify the effort setting reaches the provider (the OpenAI-compatible endpoint ignores it) and the answer and
    its tokens come back in the form the trace prices.

    id: TST-ANTH-002
    Given: LLM_PROVIDER naming anthropic, a recording client and LLM_REASONING_EFFORT=medium
    When: An LLM call is made
    Then: The request carries that effort, no temperature and a room for the answer; the client makes no retries of
          its own; the text block is returned; cached input is counted inside the prompt tokens
    """
    monkeypatch.setenv("LLM_REASONING_EFFORT", "medium")
    seen = {}
    monkeypatch.setattr(agent_orchestrator, "record_llm_meta", lambda **meta: seen.update(meta))
    assert _REAL_CALL_GEMINI("the prompt", stage="s") == "the answer"
    request = anthropic_client.sent[0]
    assert request["output_config"] == {"effort": "medium"}
    assert request["messages"] == [{"role": "user", "content": "the prompt"}]
    assert "temperature" not in request and request["max_tokens"] > 0 and request["timeout"] == 180.0
    assert request["model"] == llm_provider.PROVIDERS["anthropic"].model
    assert anthropic_client.built[0] == {"api_key": "claude-key", "max_retries": 0}
    assert (seen["prompt_tokens"], seen["completion_tokens"], seen["total_tokens"], seen["cached_tokens"]) == (
        120, 40, 160, 20)
    assert seen["finish_reason"] == "end_turn" and seen["reasoning_effort"] == "medium"


def test_an_empty_effort_sends_none_and_a_schema_holds_the_answer(anthropic_client, monkeypatch):
    """Verify a stage with a typed answer has the provider hold the answer to its schema.

    id: TST-ANTH-003
    Given: LLM_REASONING_EFFORT set to empty, and a call with a json_schema
    When: The call is made
    Then: The request carries the schema as the output format, every object closed to other properties (the provider
          requires that), and no effort
    """
    monkeypatch.setenv("LLM_REASONING_EFFORT", "")
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    _REAL_CALL_GEMINI("p", stage="s", json_mode=True, json_schema=schema)
    sent = anthropic_client.sent[0]["output_config"]
    assert set(sent) == {"format"} and sent["format"]["type"] == "json_schema"
    assert sent["format"]["schema"]["properties"] == schema["properties"]
    assert sent["format"]["schema"]["additionalProperties"] is False
    assert "additionalProperties" not in schema


def test_images_follow_the_prompt_as_image_blocks(anthropic_client, tmp_path):
    """Verify a call that shows screenshots sends them in the provider's own form.

    id: TST-ANTH-004
    Given: A PNG file
    When: A call is made with it as an image
    Then: The message is the prompt followed by a base64 PNG image block
    """
    png = tmp_path / "shot.png"
    png.write_bytes(b"png-bytes")
    _REAL_CALL_GEMINI("look", stage="s", images=[str(png)])
    assert anthropic_client.sent[0]["messages"][0]["content"] == [
        {"type": "text", "text": "look"},
        {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                     "data": base64.b64encode(b"png-bytes").decode("ascii")}}]


def test_a_provider_error_fails_loudly_with_its_reason(anthropic_client):
    """Verify a failed call returns nothing and names why, as for every other provider.

    id: TST-ANTH-005
    Given: A client that raises
    When: A call is made
    Then: The answer is empty, LAST_LLM_ERROR carries the reason, and one request was made
    """
    anthropic_client.answer = RuntimeError("overloaded")
    assert _REAL_CALL_GEMINI("p", stage="s") == ""
    assert "overloaded" in agent_orchestrator.LAST_LLM_ERROR and len(anthropic_client.sent) == 1


def test_calls_made_side_by_side_stay_under_the_providers_limit(anthropic_client, monkeypatch):
    """Verify stages that call the provider at once wait their turn instead of being refused.

    id: TST-ANTH-006
    Given: A provider that takes time to answer, and more calls started at once than it accepts side by side
    When: All of them run
    Then: Every call is answered, and never more than the limit were in flight together
    """
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor

    monkeypatch.setattr(llm_anthropic, "_in_flight", threading.BoundedSemaphore(3))
    lock, now, peak = threading.Lock(), [0], [0]
    answer = anthropic_client.answer

    def slow_create(self, **kwargs):
        with lock:
            now[0] += 1
            peak[0] = max(peak[0], now[0])
        time.sleep(0.05)
        with lock:
            now[0] -= 1
        return answer

    monkeypatch.setattr(anthropic_client, "_create", slow_create)
    with ThreadPoolExecutor(max_workers=12) as pool:
        answers = list(pool.map(lambda _: llm_anthropic.complete("k", "m", "p", None, "low", None, 5.0)[0], range(12)))
    assert answers == ["the answer"] * 12 and peak[0] == 3
