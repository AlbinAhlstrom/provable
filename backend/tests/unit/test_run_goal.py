"""Unit tests for the goal score of a run (backend/run_goal.py): a valid app at 1 SEK in 120 s is 100%."""

import json

import pytest

import run_goal
import run_recorder
from tests.unit.test_run_recorder import _llm, runs_root, workspace  # noqa: F401  (fixtures)


def test_a_valid_app_scores_its_cost_and_time_against_the_goal():
    """Verify the score falls in proportion to cost and time over the goal, and is 0 for an invalid app.

    id: TST-GOAL-001
    Given: Runs at, under and over the goal of 1 SEK and 120 s
    When: Each is scored
    Then: Twice the cost or time halves the score, under the goal counts as the goal, an invalid app scores 0
    """
    assert run_goal.score(valid=True, cost_sek=1.0, wall_s=120) == 100.0
    assert run_goal.score(valid=True, cost_sek=0.5, wall_s=60) == 100.0
    assert run_goal.score(valid=True, cost_sek=2.0, wall_s=120) == 50.0
    assert run_goal.score(valid=True, cost_sek=2.0, wall_s=240) == 25.0
    assert run_goal.score(valid=False, cost_sek=0.5, wall_s=60) == 0.0
    assert run_goal.score(valid=True, cost_sek=None, wall_s=60) is None


def _summary(run_dir):
    return json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("success, score", [(True, 50.0), (False, 0.0)])
def test_the_rule_tests_after_a_kickstart_record_the_goal_score_of_both(runs_root, workspace, monkeypatch,
                                                                          success, score):
    """Verify the rule-tests run scores the kickstart it follows together with itself.

    id: TST-GOAL-002
    Given: A kickstart run, then a rule-tests run whose rules all pass (or one fails)
    When: The rule-tests run finishes
    Then: Its summary holds the goal: the kickstart scored, the app valid only when every rule passed,
          the cost and wall time of both added up, and the score from them
    """
    monkeypatch.setattr(run_recorder, "llm_totals", lambda trace_dir: {"calls": 1, "cost_sek": 1.0})
    monkeypatch.setattr(run_goal, "GOAL_S", 10_000)  # the test's runs take milliseconds: time stays inside the goal

    with run_recorder.recorded_run("kickstart", "pitch", workspace_dir=str(workspace)) as run:
        run.result = {"success": True}
        kickstart = run.id
    with run_recorder.recorded_run("rule_tests", "after kickstart", workspace_dir=str(workspace)) as run:
        run.result = {"success": success}
        rule_tests = run.id

    first, second = _summary(runs_root / kickstart), _summary(runs_root / rule_tests)
    goal = second["goal"]
    assert goal["kickstart"] == kickstart
    assert goal["valid"] is success
    assert goal["cost_sek"] == 2.0
    assert goal["wall_s"] == round(first["duration_s"] + second["duration_s"], 2)
    assert goal["score_pct"] == score


def test_a_run_of_its_own_records_no_goal_score(runs_root, workspace):
    """Verify only the rule tests that follow a kickstart are scored: a kickstart alone cannot tell valid yet.

    id: TST-GOAL-003
    Given: A kickstart run, and rule tests run by hand with no kickstart before them
    When: Each finishes
    Then: Neither summary holds a goal
    """
    with run_recorder.recorded_run("rule_tests", "deck", workspace_dir=str(workspace)) as run:
        alone = run.id
    with run_recorder.recorded_run("kickstart", "pitch", workspace_dir=str(workspace)) as run:
        kickstart = run.id
    assert "goal" not in _summary(runs_root / alone)
    assert "goal" not in _summary(runs_root / kickstart)
