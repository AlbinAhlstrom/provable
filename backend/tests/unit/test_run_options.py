"""What one run is asked to do differently from the settings (`run_options.py`): strict, and one model throughout."""
from types import SimpleNamespace

import llm_provider
import run_options
import run_recorder
from onboarding import kickstart_front

OPUS = "claude-opus-5-5"


def test_a_run_on_one_model_asks_every_stage_of_it(monkeypatch):
    """
    id: TST-RUNOPT-MODEL
    Given: The Anthropic provider, which puts the contract stages on another model than the rest
    When: A run is held on one model, and after it
    Then: Inside it every stage, the contract stages too, is asked of that model, and thinks; after it the provider's
          models are back
    """
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    before = {stage: llm_provider.connection(stage).model for stage in ("product_contract", "first_tests")}
    assert before["product_contract"] != before["first_tests"]
    with run_options.running_with(run_options.RunOptions(model=OPUS)):
        for stage in ("product_contract", "first_tests", "general"):
            assert llm_provider.connection(stage).model == OPUS
            assert llm_provider.connection(stage).thinking
    assert {stage: llm_provider.connection(stage).model for stage in before} == before


def test_the_run_record_says_how_the_run_was_asked(monkeypatch, tmp_path):
    """
    id: TST-RUNOPT-RECORDED
    Given: A strict run on one model, recorded
    When: Its run.json is read
    Then: It names both options
    """
    import json
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    with run_options.running_with(run_options.RunOptions(strict=True, model=OPUS)):
        with run_recorder.recorded_run("kickstart", "p") as run:
            folder = run.dir
    with open(f"{folder}/run.json", encoding="utf-8") as f:
        asked = json.load(f)
    assert asked["options"] == {"strict": True, "model": OPUS}


def test_a_strict_run_builds_the_plan_as_written(monkeypatch):
    """
    id: TST-RUNOPT-PLAN
    Given: A strict run, and a plan whose review finds a conflict
    When: The plan is reviewed
    Then: It is not sent back to be written again: the plan is built as written and the conflict stays reported
    """
    contract = SimpleNamespace(specs=lambda: [], intent=lambda: None)
    found = {"success": True, "conflicts": [{"specs": ["SPEC-001", "SPEC-002"], "reason": "they disagree"}]}
    reworked = []
    with run_options.running_with(run_options.RunOptions(strict=True)):
        plan, review = kickstart_front.reviewed_plan(contract, review=lambda specs, intent: found,
                                                     rework=lambda c, conflicts: reworked.append(1) or c)
    assert reworked == [] and plan is contract and review == found
