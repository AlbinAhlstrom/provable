"""Unit tests for the stages between the skeleton and styling (backend/onboarding/synthesis_stages.py)."""

import json
import threading

import pytest

import run_recorder
from onboarding.action_behaviour import ActionBehaviour
from onboarding.spec_runner import SpecRun
from onboarding.synthesis_stages import run_synthesis_stages

WAIT = 5  # seconds a fake waits for its peer before the test fails instead of hanging


def _stages(**overrides):
    stages = dict(
        review=lambda specs, intent=None: {"success": True, "conflicts": []},
        protocol=lambda **kw: {"success": True, "files": [], "action_manifest": {"actions": [{"name": "submit"}]}},
        seed=lambda **kw: {"success": True, "files": ["seed.json"]},
        presentation=lambda **kw: {"success": True, "files": ["App.tsx"]},
        ux=lambda **kw: "### 1. Plan\n### 6. Visual Direction\nwarm cream, one amber accent",
        behaviour=lambda manifest, workspace_dir, rules=None: ActionBehaviour(implemented=["submit"]),
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
                      "action_behaviour": "ok", "behaviour_specs": "skipped", "presentation": "failed",
                      "page_revisit": "skipped", "rule_tests": "skipped"}


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


CLASS = "from dataclasses import dataclass\n\n\n@dataclass\nclass Inquiry:\n    id: str\n    status: str = 'new'\n"


def _domain_class(workspace, source=CLASS):
    path = workspace / "src" / "domain" / "inquiry.py"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    return path


def _stage_records(tmp_path):
    run = next(p for p in (tmp_path / "runs").iterdir() if p.is_dir())
    return {s["name"]: s for s in json.loads((run / "summary.json").read_text(encoding="utf-8"))["stages"]}


def test_the_page_is_written_while_its_actions_are_implemented(tmp_path):
    """Verify the page no longer waits for the methods behind its actions.

    id: TST-SYN-BEHAVIOUR
    Given: A behaviour stage that only finishes once the presentation has started, and a presentation that only
           finishes once the behaviour stage has started
    When: The stages run
    Then: Both finish (one after the other, either would wait forever); behaviour ran with the protocol's manifest
          and its result is in the outcome
    """
    seen, behaviour_started, page_started = [], threading.Event(), threading.Event()

    def behaviour(manifest, workspace_dir, rules=None):
        seen.append([a["name"] for a in manifest["actions"]])
        behaviour_started.set()
        assert page_started.wait(WAIT), "the page waited for its actions to be implemented"
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        page_started.set()
        assert behaviour_started.wait(WAIT), "the actions were not implemented alongside the page"
        return {"success": True, "files": ["App.tsx"]}

    outcome = _run(tmp_path, behaviour=behaviour, presentation=presentation)
    assert seen == [["submit"]]
    assert outcome.behaviour.implemented == ["submit"] and outcome.failures == []


def test_a_page_whose_classes_kept_their_fields_is_not_written_again(tmp_path, monkeypatch):
    """Verify the usual case costs one page: the methods were written and the classes hold what they held.

    id: TST-SYN-REVISIT-UNCHANGED
    Given: A domain class to which the behaviour stage adds a method and no field, in a recorded run
    When: The stages run
    Then: The page is written once, and the revisit is recorded as skipped with the reason
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    workspace = tmp_path / "ws"
    domain_class = _domain_class(workspace)
    pages = []

    def behaviour(manifest, workspace_dir, rules=None):
        domain_class.write_text(CLASS + "\n    def submit(self) -> None:\n        self.status = 'sent'\n", encoding="utf-8")
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        pages.append(domain_class.read_text(encoding="utf-8"))
        return {"success": True, "files": []}

    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        outcome = _run(workspace, behaviour=behaviour, presentation=presentation)
    assert len(pages) == 1 and outcome.failures == [] and outcome.page_revisit == []
    revisit = _stage_records(tmp_path)["page_revisit"]
    assert revisit["status"] == "skipped" and "hold the fields the page was written for" in revisit["error"]


def test_a_page_is_written_again_when_a_class_holds_something_new(tmp_path, monkeypatch):
    """Verify a class that changed under the page sends the page back once, to be written for the class as it is.

    id: TST-SYN-REVISIT-CHANGED
    Given: A domain class to which the behaviour stage adds a field the page could not know of, in a recorded run
    When: The stages run
    Then: The page is written a second time, after the actions, against the class with the new field; the outcome
          and the revisit's record name what changed, and the second page is the one that stands
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    workspace = tmp_path / "ws"
    domain_class = _domain_class(workspace)
    pages = []

    def behaviour(manifest, workspace_dir, rules=None):
        domain_class.write_text(CLASS + "    answered_by: str = ''\n", encoding="utf-8")
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        pages.append("answered_by" in domain_class.read_text(encoding="utf-8"))
        return {"success": True, "files": [f"Page{len(pages)}.tsx"]}

    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        outcome = _run(workspace, behaviour=behaviour, presentation=presentation)
    assert len(pages) == 2 and pages[1] is True
    assert outcome.page_revisit == ["Inquiry now also holds answered_by"]
    assert outcome.presentation["files"] == ["Page2.tsx"] and outcome.failures == []
    records = _stage_records(tmp_path)
    assert records["presentation"]["status"] == "ok" and records["page_revisit"]["status"] == "ok"
    assert records["page_revisit"]["notes"]["changed"] == ["Inquiry now also holds answered_by"]


def test_a_revisit_that_does_not_deliver_leaves_the_first_page(tmp_path):
    """Verify a failed second writing is reported and costs nothing that was there.

    id: TST-SYN-REVISIT-FAILED
    Given: A class that changed under the page, and a presentation whose second call fails
    When: The stages run
    Then: The failure names the revisit and its reason, and the outcome still carries the first page
    """
    domain_class = _domain_class(tmp_path)
    calls = []

    def behaviour(manifest, workspace_dir, rules=None):
        domain_class.write_text(CLASS + "    answered_by: str = ''\n", encoding="utf-8")
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        calls.append(1)
        return {"success": True, "files": ["Page.tsx"]} if len(calls) == 1 else {"success": False, "error": "quota", "files": []}

    outcome = _run(tmp_path, behaviour=behaviour, presentation=presentation)
    assert outcome.failures == [{"stage": "page_revisit", "error": "quota"}]
    assert outcome.presentation == {"success": True, "files": ["Page.tsx"]}


def test_a_page_that_was_not_written_is_not_revisited(tmp_path):
    """Verify the revisit is not a second chance for a page that failed: that failure stands as it is.

    id: TST-SYN-REVISIT-NO-PAGE
    Given: A class that changed while the page was being written, and a presentation that fails
    When: The stages run
    Then: The presentation is called once and its failure is the only one
    """
    domain_class = _domain_class(tmp_path)
    calls = []

    def behaviour(manifest, workspace_dir, rules=None):
        domain_class.write_text(CLASS + "    answered_by: str = ''\n", encoding="utf-8")
        return ActionBehaviour(implemented=["submit"])

    def presentation(**kw):
        calls.append(1)
        return {"success": False, "error": "no App.tsx", "files": []}

    outcome = _run(tmp_path, behaviour=behaviour, presentation=presentation)
    assert len(calls) == 1 and outcome.failures == [{"stage": "presentation", "error": "no App.tsx"}]


def test_an_action_nothing_implements_is_a_reported_failure_and_the_page_is_still_written(tmp_path):
    """Verify a missing action degrades the run loudly without stopping the page.

    id: TST-SYN-BEHAVIOUR-MISSING
    Given: A behaviour stage that leaves one action without a method
    When: The stages run
    Then: The failure names the stage and the action, and the presentation still delivered
    """
    missing = ActionBehaviour(missing=[{"action": "submit", "aggregate": "Inquiry", "performed_by": "audience"}],
                              runs=[{"aggregate": "Inquiry", "status": "REQUIRES_HUMAN_INTERVENTION", "error": "assert failed"}])
    outcome = _run(tmp_path, behaviour=lambda manifest, workspace_dir, rules=None: missing)
    assert [f["stage"] for f in outcome.failures] == ["action_behaviour"]
    assert "submit" in outcome.failures[0]["error"]
    assert outcome.presentation["success"]


def test_the_rule_specs_run_after_the_actions_and_while_the_page_is_written(tmp_path):
    """Verify the specs build on the actions' methods and do not queue in front of the presentation.

    id: TST-SYN-SPECS
    Given: A spec stage that checks the actions are implemented, and a presentation that only finishes once it started
    When: The stages run
    Then: Both finish, and the spec result is in the outcome before the stages return (QA runs on a settled domain)
    """
    order, specs_started = [], threading.Event()

    def behaviour(manifest, workspace_dir, rules=None):
        order.append("behaviour")
        return ActionBehaviour(implemented=["submit"])

    def specs(inbox_specs, report, drafted):
        assert order == ["behaviour"], "the specs ran before the actions were implemented"
        specs_started.set()
        return SpecRun(fulfilled=["SPEC-001"])

    def presentation(**kw):
        assert specs_started.wait(WAIT), "the specs did not run alongside the presentation"
        return {"success": True, "files": ["App.tsx"]}

    outcome = _run(tmp_path, behaviour=behaviour, specs=specs, presentation=presentation)
    assert outcome.specs.fulfilled == ["SPEC-001"] and outcome.failures == []


def test_a_spec_that_was_not_fulfilled_is_a_reported_failure(tmp_path):
    """Verify a rule the app does not enforce degrades the run by name.

    id: TST-SYN-SPECS-UNFULFILLED
    Given: A spec stage with one spec that did not reach GREEN
    When: The stages run
    Then: The failure names the stage and the spec, and the presentation still delivered
    """
    unfulfilled = SpecRun(unfulfilled=[{"spec_id": "SPEC-002", "title": "No double booking", "status": "REQUIRES_HUMAN_INTERVENTION",
                                        "error": "assert raised"}])
    outcome = _run(tmp_path, specs=lambda inbox_specs, report, drafted: unfulfilled)
    assert [f["stage"] for f in outcome.failures] == ["behaviour_specs"]
    assert "SPEC-002" in outcome.failures[0]["error"] and outcome.presentation["success"]


def test_the_ux_plans_palette_is_written_as_the_drafts_theme(tmp_path):
    """Verify the app on screen takes the plan's colours as soon as the plan is there.

    id: TST-SYN-DRAFT-THEME
    Given: A skeleton's neutral theme file, and a UX plan whose visual direction ends with its token line
    When: The stages run
    Then: The theme file holds the plan's background colour
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "theme.css").write_text(":root {}", encoding="utf-8")
    plan = ("### 6. Visual Direction\nwarm cream\n"
            "TOKENS background=#faf7f2 surface=#ffffff text=#1c1917 accent=#b45309 on_accent=#ffffff heading=serif")
    _run(tmp_path, ux=lambda **kw: plan)
    assert "--draft-bg: #faf7f2;" in (tmp_path / "src" / "theme.css").read_text(encoding="utf-8")


def test_the_ux_plans_layout_is_drawn_in_the_draft_even_without_a_palette(tmp_path):
    """Verify the app on screen shows the outline of its main view as soon as the plan states it.

    id: TST-SYN-DRAFT-LAYOUT
    Given: A skeleton's neutral theme file, and a UX plan that states a layout but no token line
    When: The stages run
    Then: The theme file draws the outline, in the neutral colours
    """
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "theme.css").write_text(":root {}", encoding="utf-8")
    _run(tmp_path, ux=lambda **kw: "### 6. Visual Direction\nwarm cream\nLAYOUT columns=7 rows=5")
    css = (tmp_path / "src" / "theme.css").read_text(encoding="utf-8")
    assert "aspect-ratio: 7 / 5;" in css and "--draft-bg:" in css


def test_a_component_the_page_does_not_use_is_no_longer_reported_as_written(tmp_path, monkeypatch):
    """Verify later stages are only handed files that still exist.

    id: TST-SYN-REMOVED-COMPONENT
    Given: A presentation that wrote a view and a component its page never imports, which the cleanup then removes
    When: The stages run
    Then: The presentation's files, and the outcome's, list the view and not the removed component
    """
    import onboarding.synthesis_stages as stages_module

    view, unused = tmp_path / "src" / "View.tsx", tmp_path / "src" / "Unused.tsx"
    view.parent.mkdir(parents=True)
    view.write_text("export {}", encoding="utf-8")
    unused.write_text("export {}", encoding="utf-8")

    def cleanup(workspace_dir):
        unused.unlink()
        return ["src/Unused.tsx"]

    monkeypatch.setattr(stages_module, "remove_unreachable", cleanup)
    outcome = _run(tmp_path, presentation=lambda **kw: {"success": True, "files": [str(view), str(unused)]})
    assert outcome.presentation["files"] == [str(view)]
    assert str(unused) not in outcome.files and outcome.removed_scaffold == ["src/Unused.tsx"]


def test_rules_are_not_written_when_there_is_no_action_protocol(tmp_path):
    """Verify a failed action protocol stops the rules too: nothing was implemented for them to build on.

    id: TST-SYN-SPECS-NO-PROTOCOL
    Given: An action protocol stage that fails (its answer could not be read)
    When: The stages run
    Then: The spec executor is never called; the only failure is the action protocol's
    """
    def specs(inbox_specs, report, drafted):
        raise AssertionError("the rules ran on a class without its actions")

    outcome = _run(tmp_path, protocol=lambda **kw: {"success": False, "error": "not valid JSON", "files": []}, specs=specs)
    assert [f["stage"] for f in outcome.failures] == ["action_protocol"]


def test_the_rules_first_tests_are_written_while_the_actions_are_implemented(tmp_path):
    """Verify the rule deck's test writing no longer waits for the actions' methods.

    id: TST-SYN-DRAFTS
    Given: A behaviour stage that only finishes once the test writer has started, and a spec stage that records the
           drafts it is handed
    When: The stages run
    Then: All of them finish (after the actions, the test writer would never have started), and the spec stage was
          given the drafted tests
    """
    drafting, handed = threading.Event(), []

    def drafts(inbox_specs):
        drafting.set()
        return {"SPEC-001": "def test_rule(): ..."}

    def behaviour(manifest, workspace_dir, rules=None):
        assert drafting.wait(WAIT), "the rules' tests were not written alongside the actions"
        return ActionBehaviour(implemented=["submit"])

    def specs(inbox_specs, report, drafted):
        handed.append(drafted)
        return SpecRun(fulfilled=["SPEC-001"])

    outcome = _run(tmp_path, drafts=drafts, behaviour=behaviour, specs=specs)
    assert handed == [{"SPEC-001": "def test_rule(): ..."}] and outcome.failures == []


def test_no_tests_are_drafted_without_an_action_protocol(tmp_path):
    """Verify the test writer is not paid for rules that will not run.

    id: TST-SYN-DRAFTS-NO-PROTOCOL
    Given: An action protocol stage that fails
    When: The stages run
    Then: The test writer is never called
    """
    def drafts(inbox_specs):
        raise AssertionError("tests were written for a class whose actions are not named")

    outcome = _run(tmp_path, protocol=lambda **kw: {"success": False, "error": "not valid JSON", "files": []}, drafts=drafts)
    assert [f["stage"] for f in outcome.failures] == ["action_protocol"]
