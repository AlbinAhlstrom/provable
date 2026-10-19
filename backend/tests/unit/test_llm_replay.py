"""Unit tests for replaying recorded LLM answers (backend/llm_replay.py): a run that names a recorded run is answered
from it wherever it asks exactly what that run asked, and asks the model everything else."""

import json

import pytest

import agent_orchestrator
import llm_replay
import run_recorder

# Captured at import time, before conftest's autouse fixture swaps in the hermetic mock.
_REAL_CALL_GEMINI = agent_orchestrator.call_gemini
SCHEMA = {"type": "object", "properties": {"a": {"type": "string"}}}


class _Provider:
    """A provider that answers `answer-<n>` to its n-th question, and remembers what it was asked."""

    def __init__(self):
        self.asked = []
        provider = self

        class Completions:
            def create(self, **kwargs):
                provider.asked.append(kwargs)
                msg = type("M", (), {"content": f"answer-{len(provider.asked)}"})()
                choice = type("C", (), {"message": msg, "finish_reason": "stop"})()
                return type("R", (), {"choices": [choice], "usage": None})()

        class Client:
            def __init__(self, **_):
                self.chat = type("Chat", (), {"completions": Completions()})()

        self.client = Client


@pytest.fixture
def provider(monkeypatch, tmp_path):
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    monkeypatch.setenv("LLM_REASONING_EFFORT", "low")
    fake = _Provider()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", fake.client)
    return fake


def _record(tmp_path, calls):
    """Runs `calls` (each `(prompt, options)`) as one recorded run and answers its id."""
    (tmp_path / "ws").mkdir(exist_ok=True)
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(tmp_path / "ws")) as run:
        answers = [_REAL_CALL_GEMINI(prompt, **options) for prompt, options in calls]
    return run.id, answers


def _summary(run_id):
    with open(f"{run_recorder.runs_root()}/{run_id}/summary.json", encoding="utf-8") as f:
        return json.load(f)


def test_a_run_asking_what_a_recorded_run_asked_is_answered_from_it(provider, tmp_path):
    """Verify the cost of iterating on one stage: every other stage asks what it asked before, and is answered from
    the recorded run instead of the model.

    id: TST-REPLAY-001
    Given: A recorded run that asked one question
    When: A run naming it asks the same question
    Then: The recorded answer comes back, the model is not asked, and the run counts the call as replayed, at no
          cost, and names the run it replays
    """
    recorded, _ = _record(tmp_path, [("p", {"stage": "contract", "json_mode": True, "json_schema": SCHEMA})])
    asked = len(provider.asked)

    with llm_replay.replaying([recorded]):
        again, answers = _record(tmp_path, [("p", {"stage": "contract", "json_mode": True, "json_schema": SCHEMA})])

    assert answers == ["answer-1"] and len(provider.asked) == asked
    llm = _summary(again)["llm"]
    assert llm["calls"] == 1 and llm["replayed"] == 1 and llm["cost_sek"] == 0
    assert llm["by_stage"]["contract"]["replayed"] == 1
    with open(f"{run_recorder.runs_root()}/{again}/run.json", encoding="utf-8") as f:
        assert json.load(f)["llm"]["replay"] == [recorded]


@pytest.mark.parametrize("prompt, options", [
    ("p changed", {"stage": "contract", "json_mode": True, "json_schema": SCHEMA}),
    ("p", {"stage": "review", "json_mode": True, "json_schema": SCHEMA}),
    ("p", {"stage": "contract", "json_mode": True, "json_schema": {**SCHEMA, "required": ["a"]}}),
    ("p", {"stage": "contract", "json_mode": True, "json_schema": SCHEMA, "reasoning_effort": "medium"}),
])
def test_a_question_that_differs_in_anything_the_model_sees_is_asked_of_the_model(provider, tmp_path, prompt, options):
    """Verify nothing stale comes back: a changed prompt, stage, schema or effort is a new question.

    id: TST-REPLAY-002
    Given: A recorded run that asked one question
    When: A run naming it asks a question that differs in its prompt, stage, schema or effort
    Then: The model answers it, and the call is not counted as replayed
    """
    recorded, _ = _record(tmp_path, [("p", {"stage": "contract", "json_mode": True, "json_schema": SCHEMA})])

    with llm_replay.replaying([recorded]):
        again, answers = _record(tmp_path, [(prompt, options)])

    assert answers == ["answer-2"]
    assert _summary(again)["llm"]["replayed"] == 0


def test_a_question_on_another_model_is_asked_of_the_model(provider, tmp_path, monkeypatch):
    """
    id: TST-REPLAY-003
    Given: A recorded run that asked one question
    When: A run naming it asks the same question of another model
    Then: The model answers it
    """
    recorded, _ = _record(tmp_path, [("p", {"stage": "contract"})])
    monkeypatch.setenv("LLM_MODEL_CONTRACT", "another-model")

    with llm_replay.replaying([recorded]):
        _, answers = _record(tmp_path, [("p", {"stage": "contract"})])

    assert answers == ["answer-2"]


def test_a_question_asked_twice_gets_its_answers_in_the_order_they_were_given(provider, tmp_path):
    """Verify a question asked more than once is answered as it was then, and once they are used up, by the model.

    id: TST-REPLAY-004
    Given: A recorded run that asked the same question twice and got two answers
    When: A run naming it asks that question three times
    Then: The first two answers come back in order and the model answers the third
    """
    recorded, _ = _record(tmp_path, [("p", {"stage": "s"}), ("p", {"stage": "s"})])

    with llm_replay.replaying([recorded]):
        _, answers = _record(tmp_path, [("p", {"stage": "s"})] * 3)

    assert answers == ["answer-1", "answer-2", "answer-3"]


def test_a_question_with_screenshots_or_a_failed_answer_is_never_replayed(provider, tmp_path, monkeypatch):
    """Verify a recording replays only what it holds whole: its trace keeps a screenshot's path, not the picture,
    and a call that failed holds no answer.

    id: TST-REPLAY-005
    Given: A recorded run that asked a question with a screenshot, and one whose answer failed
    When: A run naming it asks both again
    Then: The model answers both
    """
    shot = tmp_path / "shot.png"
    shot.write_bytes(b"png")
    recorded, _ = _record(tmp_path, [("look", {"stage": "visual", "images": [str(shot)]})])
    monkeypatch.setattr(agent_orchestrator, "OpenAI", None)  # the provider is unreachable: the call fails
    failed, answers = _record(tmp_path, [("p", {"stage": "s"})])
    assert answers == [""]
    monkeypatch.setattr(agent_orchestrator, "OpenAI", provider.client)

    with llm_replay.replaying([recorded, failed]):
        _, answers = _record(tmp_path, [("look", {"stage": "visual", "images": [str(shot)]}), ("p", {"stage": "s"})])

    assert answers == ["answer-2", "answer-3"]


def test_a_run_to_replay_that_does_not_exist_fails_loudly(provider):
    """
    id: TST-REPLAY-006
    Given: No recorded run of that name
    When: A run names it to replay
    Then: It fails by name before anything is asked
    """
    with pytest.raises(ValueError, match="no-such-run"):
        with llm_replay.replaying(["no-such-run"]):
            pass


def test_without_a_run_to_replay_every_question_is_asked_of_the_model(provider, tmp_path):
    """
    id: TST-REPLAY-007
    Given: A recorded run
    When: The same question is asked again without naming it
    Then: The model answers
    """
    _record(tmp_path, [("p", {"stage": "s"})])
    _, answers = _record(tmp_path, [("p", {"stage": "s"})])
    assert answers == ["answer-2"]


def test_a_kickstart_names_the_runs_it_replays_and_its_page_tests_replay_them_too(monkeypatch):
    """Verify replay is asked for on the request, so the running engine needs no restart, and reaches the page
    tests that follow the kickstart.

    id: TST-REPLAY-008
    Given: A kickstart request that names two recorded runs
    When: The kickstart runs and its page tests follow
    Then: Both run while those runs are replayed, and nothing is replayed afterwards
    """
    from fastapi import BackgroundTasks
    from entrypoints.routers import onboarding
    from service_layer import rule_tests, services
    seen = {}
    monkeypatch.setattr(llm_replay, "_load", lambda run_id: {})
    monkeypatch.setattr(services, "kickstart_domain_and_scaffold",
                        lambda **kwargs: seen.update(kickstart=llm_replay.active()) or {"success": True, "qa": {}})
    monkeypatch.setattr(rule_tests, "run_all_rule_tests",
                        lambda **kwargs: seen.update(page_tests=llm_replay.active()))
    background = BackgroundTasks()

    onboarding.kickstart_endpoint(onboarding.KickstartRequest(pitch="p", replay=["k1", "t1"]), background)
    for task in background.tasks:
        task.func(*task.args, **task.kwargs)

    assert seen == {"kickstart": ["k1", "t1"], "page_tests": ["k1", "t1"]}
    assert llm_replay.active() == []


def test_a_stage_named_live_is_asked_of_the_model_while_the_rest_is_replayed(provider, tmp_path):
    """Verify one stage can be sampled again on the same recorded input: how much of a run's variance is its own.

    id: TST-REPLAY-009
    Given: A recorded run that asked two stages
    When: A run replays it with one of them named live
    Then: That stage is asked of the model, the other is answered from the record, and the run says which was live
    """
    recorded, _ = _record(tmp_path, [("p", {"stage": "contract"}), ("q", {"stage": "page"})])

    with llm_replay.replaying([recorded], live=["page"]):
        again, answers = _record(tmp_path, [("p", {"stage": "contract"}), ("q", {"stage": "page"})])

    assert answers == ["answer-1", "answer-3"]
    with open(f"{run_recorder.runs_root()}/{again}/run.json", encoding="utf-8") as f:
        assert json.load(f)["llm"]["replay_live"] == ["page"]


def test_a_kickstart_names_the_stages_to_ask_live_and_its_page_tests_keep_them(monkeypatch):
    """
    id: TST-REPLAY-010
    Given: A kickstart request that names a recorded run and a stage to ask live
    When: The kickstart runs and its page tests follow
    Then: Both run with that stage live
    """
    from fastapi import BackgroundTasks
    from entrypoints.routers import onboarding
    from service_layer import rule_tests, services
    seen = {}
    monkeypatch.setattr(llm_replay, "_load", lambda run_id: {})
    monkeypatch.setattr(services, "kickstart_domain_and_scaffold",
                        lambda **kwargs: seen.update(kickstart=llm_replay.live()) or {"success": True, "qa": {}})
    monkeypatch.setattr(rule_tests, "run_all_rule_tests", lambda **kwargs: seen.update(page_tests=llm_replay.live()))
    background = BackgroundTasks()

    onboarding.kickstart_endpoint(
        onboarding.KickstartRequest(pitch="p", replay=["k1"], replay_live=["page_test_generation"]), background)
    for task in background.tasks:
        task.func(*task.args, **task.kwargs)

    assert seen == {"kickstart": ["page_test_generation"], "page_tests": ["page_test_generation"]}
    assert llm_replay.live() == []
