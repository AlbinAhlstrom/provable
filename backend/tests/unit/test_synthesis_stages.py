"""Unit tests for the stages between the skeleton and styling (backend/onboarding/synthesis_stages.py)."""

import json
import threading

import pytest

import run_recorder
from onboarding.action_behaviour import ActionBehaviour
from onboarding.synthesis_stages import run_synthesis_stages

WAIT = 5  # seconds a fake waits for its peer before the test fails instead of hanging


def _stages(**overrides):
    stages = dict(
        review=lambda specs, intent=None: {"success": True, "conflicts": []},
        protocol=lambda **kw: {"success": True, "files": [], "action_manifest": {"actions": [{"name": "submit"}]}},
        seed=lambda **kw: {"success": True, "files": ["seed.json"]},
        presentation=lambda **kw: {"success": True, "files": ["App.tsx"]},
        ux=lambda **kw: "### 1. Plan\n### 6. Visual Direction\nwarm cream, one amber accent",
        behaviour=lambda manifest, workspace_dir: ActionBehaviour(implemented=["submit"]),
    )
    stages.update(overrides)
    return stages


def _run(tmp_path, manifests=None, **overrides):
    return run_synthesis_stages(
        pitch="p", structure=object(), inbox_specs=[], workspace_dir=str(tmp_path), intent=None,
        on_action_manifest=(manifests if manifests is not None else []).append, **_stages(**overrides))


def test_seed_data_and_spec_review_run_while_the_presentation_is_being_written(tmp_path):
    """Verify the independent stages overlap instead of queueing in front of the slowest one.

    id: TST-SYN-001
    Given: A presentation stage that only finishes once seed data and the spec review have both started
    When: The stages run
    Then: All of them finish (run one after another, the presentation would wait forever)
    """
    seed_started, review_started = threading.Event(), threading.Event()

    def seed(**kw):
        seed_started.set()
        return {"success": True, "files": []}

    def review(specs, intent=None):
        review_started.set()
        return {"success": True, "conflicts": []}

    def presentation(**kw):
        assert seed_started.wait(WAIT) and review_started.wait(WAIT), "the other stages did not run alongside"
        return {"success": True, "files": ["App.tsx"]}

    outcome = _run(tmp_path, seed=seed, review=review, presentation=presentation)
    assert outcome.presentation["success"] and outcome.failures == []
    assert outcome.files == ["App.tsx"]


def test_the_presentation_receives_the_action_protocol_and_the_manifest_is_handed_over(tmp_path):
    """Verify the one real dependency between these stages is kept.

    id: TST-SYN-002
    Given: An action protocol stage that returns a manifest
    When: The stages run
    Then: The presentation stage is called with that manifest, and the manifest is handed to the caller to store
    """
    seen, manifests = {}, []

    def presentation(**kw):
        seen.update(kw)
        return {"success": True, "files": []}

    _run(tmp_path, manifests=manifests, presentation=presentation)
    assert seen["action_manifest"] == {"actions": [{"name": "submit"}]}
    assert "warm cream" in seen["ux_blueprint"]  # the plan made alongside the protocol reaches the presentation
    assert manifests == [{"actions": [{"name": "submit"}]}]


def test_every_stage_that_does_not_deliver_is_reported_with_its_reason(tmp_path, monkeypatch):
    """Verify failures of stages that ran in parallel are all kept, each with its own reason and stage record.

    id: TST-SYN-003
    Given: A spec review, a seed stage and a presentation stage that each fail differently, in a recorded run
    When: The stages run
    Then: The outcome lists the three failures and the run summary marks exactly those stages failed
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    workspace = tmp_path / "ws"
    (workspace / "src").mkdir(parents=True)
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        outcome = _run(
            workspace,
            review=lambda specs, intent=None: {"success": False, "error": "quota"},
            seed=lambda **kw: {"success": False, "error": "the domain rejected the records twice", "files": []},
            presentation=lambda **kw: {"success": False, "error": "no App.tsx", "files": []})
    assert sorted((f["stage"], f["error"]) for f in outcome.failures) == [
        ("presentation", "no App.tsx"), ("seed_data", "the domain rejected the records twice"), ("spec_review", "quota")]
    run = next(p for p in (tmp_path / "runs").iterdir() if p.is_dir())
    stages = {s["name"]: s["status"] for s in json.loads((run / "summary.json").read_text(encoding="utf-8"))["stages"]}
    assert stages == {"spec_review": "failed", "seed_data": "failed", "ux_plan": "ok", "action_protocol": "ok",
                      "action_behaviour": "ok", "presentation": "failed"}


def test_seed_data_is_credited_with_its_file_and_the_presentation_with_its_own(tmp_path, monkeypatch):
    """Verify the run summary still says which stage wrote which file when they write at the same time.

    id: TST-SYN-004
    Given: A seed stage that writes src/seed_data.json while the presentation stage writes src/App.tsx
    When: The stages run in a recorded run
    Then: Each stage's record lists only its own file
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    workspace = tmp_path / "ws"
    (workspace / "src").mkdir(parents=True)
    seed_written = threading.Event()

    def seed(**kw):
        (workspace / "src" / "seed_data.json").write_text("{}", encoding="utf-8")
        seed_written.set()
        return {"success": True, "files": []}

    def presentation(**kw):
        assert seed_written.wait(WAIT)
        (workspace / "src" / "App.tsx").write_text("app", encoding="utf-8")
        return {"success": True, "files": []}

    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        _run(workspace, seed=seed, presentation=presentation)
    run = next(p for p in (tmp_path / "runs").iterdir() if p.is_dir())
    stages = {s["name"]: [f["path"] for f in s["files_changed"]]
              for s in json.loads((run / "summary.json").read_text(encoding="utf-8"))["stages"]}
    assert stages["seed_data"] == ["src/seed_data.json"] and stages["presentation"] == ["src/App.tsx"]
    assert stages["spec_review"] == [] and stages["action_protocol"] == []


def test_a_crash_in_a_parallel_stage_is_raised_not_lost(tmp_path):
    """Verify an unexpected exception in a background stage reaches the caller after the other stages have finished.

    id: TST-SYN-005
    Given: A seed stage that raises
    When: The stages run
    Then: The exception propagates
    """
    def seed(**kw):
        raise RuntimeError("seed crashed")

    with pytest.raises(RuntimeError, match="seed crashed"):
        _run(tmp_path, seed=seed)


def test_the_ux_plan_is_made_while_the_action_protocol_is_designed(tmp_path):
    """Verify the UX plan no longer waits for the action protocol.

    id: TST-SYN-006
    Given: An action protocol stage that only finishes once the UX plan has started
    When: The stages run
    Then: All of them finish, and the outcome carries the plan
    """
    ux_started = threading.Event()

    def ux(**kw):
        ux_started.set()
        return "### 6. Visual Direction\nink on paper"

    def protocol(**kw):
        assert ux_started.wait(WAIT), "the UX plan did not run alongside the action protocol"
        return {"success": True, "files": [], "action_manifest": {"actions": []}}

    outcome = _run(tmp_path, ux=ux, protocol=protocol)
    assert outcome.failures == [] and "ink on paper" in outcome.ux_blueprint


def test_a_written_page_leaves_no_scaffold_it_does_not_reach(tmp_path):
    """Verify the presentation stage finishes by removing the scaffold its page superseded, and says what it removed.

    id: TST-SYN-SCAFFOLD
    Given: A workspace whose app reaches one view, with a scaffold view nothing imports
    When: The stages run and the presentation succeeds; and again when the presentation fails
    Then: After the success the scaffold view is gone and reported; after the failure it is kept
    """
    def workspace(root):
        for rel, text in (("src/main.tsx", "import App from './App';\n"), ("src/App.tsx", "import './views/View';\n"),
                          ("src/views/View.tsx", "export {};\n"), ("src/views/ScaffoldView.tsx", "export {};\n")):
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    done = workspace(tmp_path / "done")
    outcome = _run(done)
    assert not (done / "src/views/ScaffoldView.tsx").exists()
    assert outcome.removed_scaffold == ["src/views/ScaffoldView.tsx"]

    failed = workspace(tmp_path / "failed")
    outcome = _run(failed, presentation=lambda **kw: {"success": False, "error": "no answer", "files": []})
    assert (failed / "src/views/ScaffoldView.tsx").exists() and outcome.removed_scaffold == []


def test_the_actions_are_implemented_before_the_page_that_calls_them_is_written(tmp_path):
    """Verify the page is written against a domain that already has its methods and fields.

    id: TST-SYN-BEHAVIOUR
    Given: A behaviour stage that records the manifest it was given, and a presentation that checks it has run
    When: The stages run
    Then: Behaviour ran with the protocol's manifest before the presentation, and its result is in the outcome
    """
    seen = []

    def behaviour(manifest, workspace_dir):
        seen.append([a["name"] for a in manifest["actions"]])
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        assert seen == [["submit"]], "the page was written before its actions were implemented"
        return {"success": True, "files": ["App.tsx"]}

    outcome = _run(tmp_path, behaviour=behaviour, presentation=presentation)
    assert outcome.behaviour.implemented == ["submit"] and outcome.failures == []


def test_an_action_nothing_implements_is_a_reported_failure_and_the_page_is_still_written(tmp_path):
    """Verify a missing action degrades the run loudly without stopping the page.

    id: TST-SYN-BEHAVIOUR-MISSING
    Given: A behaviour stage that leaves one action without a method
    When: The stages run
    Then: The failure names the stage and the action, and the presentation still delivered
    """
    missing = ActionBehaviour(missing=[{"action": "submit", "aggregate": "Inquiry", "performed_by": "audience"}],
                              runs=[{"aggregate": "Inquiry", "status": "REQUIRES_HUMAN_INTERVENTION", "error": "assert failed"}])
    outcome = _run(tmp_path, behaviour=lambda manifest, workspace_dir: missing)
    assert [f["stage"] for f in outcome.failures] == ["action_behaviour"]
    assert "submit" in outcome.failures[0]["error"]
    assert outcome.presentation["success"]
