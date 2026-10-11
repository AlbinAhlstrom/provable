"""The Studio can show an app while it is being built (backend/onboarding/build_progress.py).

A kickstart answers only when everything is done, minutes after its page was written. What the run recorder already
knows about the running build (which stages are open, which delivered) is read out as a typed progress report: is the
page there yet, how many rules are active, what is being worked on.
"""
import json
import os
from dataclasses import asdict

import pytest

from onboarding.build_progress import (DRAFT_STAGE, FINAL_CHECKS, FRONTS, PHASE_JITTER, PHASES_DONE_BY, STAGE_LABELS,
                                       STAGE_PHASES, BuildProgress, current_progress, phase_ends)

CONTRACT_FRONT, STAGED_FRONT = FRONTS
OPENING_STAGES = list(CONTRACT_FRONT + STAGED_FRONT) + [DRAFT_STAGE]          # before there is anything to show
BUILD_STAGES = [name for name in STAGE_LABELS if name not in OPENING_STAGES and name not in FINAL_CHECKS]
from onboarding.router_engine import BusinessSpec, SpecKind
from onboarding.spec_runner import run_behaviour_specs
from run_recorder import recorded_run, stage_begin


def test_nothing_is_reported_as_building_when_no_kickstart_runs():
    """Verify an idle engine says so.

    id: TST-PROGRESS-001
    Given: No run is active
    When: The progress is asked for
    Then: It is not building, has no stages and no page
    """
    progress = current_progress()
    assert isinstance(progress, BuildProgress)
    assert progress.building is False and progress.stages == [] and progress.page_ready is False
    assert progress.percent == 0.0


def _started(progress):
    return [(s.name, s.status) for s in progress.opening + progress.stages if s.status != "pending"]


def _finished_build(root, durations):
    """A recorded kickstart that went well, for the progress report to learn stage durations from."""
    os.makedirs(os.path.join(root, "earlier-build"))
    with open(os.path.join(root, "earlier-build", "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"kind": "kickstart", "status": "ok",
                   "stages": [{"name": name, "status": "ok", "duration_s": seconds} for name, seconds in durations.items()]}, f)


def test_a_running_kickstart_reports_its_stages_in_plain_words(tmp_path):
    """Verify each stage of the running build is listed with its status and a label a visitor can read.

    id: TST-PROGRESS-002
    Given: A kickstart run whose skeleton stage is done and whose presentation stage is open
    When: The progress is asked for
    Then: It is building; both stages carry their status and a label; the app can be shown as a draft, and the page
          is not ready
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        stage_begin("skeleton").ok()
        stage_begin("presentation")
        progress = current_progress()

    assert progress.building is True and progress.run_id == run.id
    assert _started(progress) == [("skeleton", "ok"), ("presentation", "running")]
    assert all(s.label and s.label != s.name for s in progress.opening + progress.stages)
    assert progress.draft_ready is True and progress.page_ready is False


def test_the_page_is_ready_once_the_presentation_stage_delivered(tmp_path):
    """Verify the Studio is told the moment there is a page to show, and why when there will be none.

    id: TST-PROGRESS-003
    Given: A run whose presentation stage delivered, and one whose presentation stage failed
    When: The progress is asked for
    Then: The first says the page is ready; the second does not, and carries the stage's reason
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("presentation").ok()
        delivered = current_progress()
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("presentation").fail("the answer has no App.tsx")
        failed = current_progress()

    assert delivered.page_ready is True
    assert failed.page_ready is False
    assert next(s for s in failed.stages if s.name == "presentation").error == "the answer has no App.tsx"


def test_a_spec_execution_is_not_reported_as_a_build(tmp_path):
    """Verify only a kickstart counts as building an app: a single spec run changes one that already exists.

    id: TST-PROGRESS-004
    Given: A recorded run of another kind
    When: The progress is asked for
    Then: It is not building
    """
    with recorded_run("spec", "SPEC-001", workspace_dir=str(tmp_path)):
        stage_begin("red")
        assert current_progress().building is False


def test_rule_progress_counts_the_specs_done_and_active(tmp_path):
    """Verify the rules are counted while they are written, so the Studio can say "2 of 3 rules active".

    id: TST-PROGRESS-005
    Given: A run whose behaviour_specs stage is running three specs: the first fulfilled, the second not
    When: The progress is asked for after the second spec
    Then: The rules show 2 done of 3, 1 of them active
    """
    specs = [BusinessSpec(spec_id=f"SPEC-00{i}", title=f"Rule {i}", description="d", given_when_then="Given a When b Then c",
                          target_aggregate="Match", kind=SpecKind.BEHAVIOR.value) for i in (1, 2, 3)]
    seen = []

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        handle = stage_begin("behaviour_specs", owns=())

        def execute(batch, done):
            for spec in batch:
                seen.append(current_progress().rules)
                done(spec, {"success": spec.spec_id == "SPEC-001", "status": "FULFILLED" if spec.spec_id == "SPEC-001" else "DEAD_END"})

        run_behaviour_specs(specs, execute, report=lambda rules: handle.note("rules", asdict(rules)))
        after = current_progress().rules

    assert (seen[0].done, seen[0].total, seen[0].active) == (0, 3, 0)   # known before the first spec starts
    assert (seen[2].done, seen[2].total, seen[2].active, seen[2].latest) == (2, 3, 1, "Rule 1")
    assert (after.done, after.total, after.active) == (3, 3, 1)


def test_progress_serialises_for_the_studio(tmp_path):
    """Verify the report crosses the API as plain data.

    id: TST-PROGRESS-006
    Given: A running kickstart with a delivered presentation
    When: The progress is turned into a dict
    Then: It has the building flag, the page flag, the stages and the rules as plain values
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("presentation").ok()
        data = current_progress().to_dict()

    assert data["building"] is True and data["page_ready"] is True and data["rules"] is None
    page = next(s for s in data["stages"] if s["name"] == "presentation")
    assert page == {"name": "presentation", "label": page["label"], "status": "ok", "error": None,
                    "weight": page["weight"], "fraction": 1.0, "phases": [], "phase": 0}
    assert isinstance(data["percent"], float)


def test_every_stage_of_the_build_is_listed_from_the_start(tmp_path):
    """Verify the Studio knows the whole road ahead, not only the stages that have begun.

    id: TST-PROGRESS-007
    Given: A kickstart that has only read the idea so far
    When: The progress is asked for
    Then: The stages of that opening are listed up to the first draft, and apart from them every stage that comes
          after it in pipeline order, the ones not begun as pending; the checks made on the finished app are
          listed apart too
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("intent").ok()
        progress = current_progress()

    assert [s.name for s in progress.opening] == list(STAGED_FRONT) + [DRAFT_STAGE]
    assert [s.name for s in progress.stages] == BUILD_STAGES
    assert [(s.name, s.status) for s in progress.final_checks] == [(name, "pending") for name in FINAL_CHECKS]
    assert {s.status for s in progress.opening + progress.stages if s.name != "intent"} == {"pending"}


def test_a_stage_the_pipeline_added_is_listed_after_the_known_ones(tmp_path):
    """Verify a stage this module has no words for still shows up, so nothing the build does is hidden.

    id: TST-PROGRESS-008
    Given: A kickstart running a stage that has no label
    When: The progress is asked for
    Then: The stage is listed last, under its own name in readable form
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("load_testing")
        progress = current_progress()

    assert (progress.stages[-1].name, progress.stages[-1].label, progress.stages[-1].status) == ("load_testing", "Load testing", "running")


def test_the_bar_fills_by_each_stages_usual_share_of_a_build(tmp_path, monkeypatch):
    """Verify a finished stage adds its usual share of the time after the first draft to the total, and that
    what comes before the draft has no share of the bar.

    id: TST-PROGRESS-009
    Given: An earlier build in which the opening took 100 seconds, and after it checking the rules took 10 and
           writing the page 30
    When: A new kickstart has ended its opening, then checked the rules, and then also written the page
    Then: The total is 0 percent, then 25, then 100; the weights sum to one
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    _finished_build(str(tmp_path / "runs"), {name: 0.0 for name in STAGE_LABELS} | {"contract": 100.0, "spec_review": 10.0, "presentation": 30.0})

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("contract").ok()
        stage_begin(DRAFT_STAGE).ok()
        opened = current_progress()
        stage_begin("spec_review").ok()
        early = current_progress()
        stage_begin("presentation").ok()
        late = current_progress()

    assert (opened.percent, early.percent, late.percent) == (0.0, 25.0, 100.0)
    assert all(s.weight == 0.0 for s in opened.opening)
    assert sum(s.weight for s in early.stages) == pytest.approx(1.0)
    assert next(s for s in early.stages if s.name == "presentation").weight == pytest.approx(0.75)


def test_a_running_stage_fills_by_the_time_it_has_spent(tmp_path, monkeypatch):
    """Verify the bar moves inside a long stage instead of standing still until the stage ends.

    id: TST-PROGRESS-010
    Given: An earlier build in which writing the page, the only stage that took time, took 30 seconds
    When: The page has been in the making for 15 seconds, and then for 90
    Then: The stage is half done, then full and no more; the total follows
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    _finished_build(str(tmp_path / "runs"), {name: 0.0 for name in STAGE_LABELS} | {"presentation": 30.0})

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        stage_begin("presentation")
        began = run.started + run.stages[0].record["t_offset_s"]
        halfway = current_progress(now=began + 15.0)
        overdue = current_progress(now=began + 90.0)

    assert next(s for s in halfway.stages if s.name == "presentation").fraction == pytest.approx(0.5)
    assert halfway.percent == 50.0
    assert next(s for s in overdue.stages if s.name == "presentation").fraction == 1.0


def test_without_earlier_builds_every_stage_is_an_equal_step(tmp_path, monkeypatch):
    """Verify the bar works on a fresh install: equal steps, and a running stage adds nothing until it ends.

    id: TST-PROGRESS-011
    Given: No recorded builds
    When: A kickstart has finished one stage and is running another
    Then: Every stage weighs the same, and the total is one stage's share
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        stage_begin("spec_review").ok()
        stage_begin("presentation")
        progress = current_progress()

    share = 1 / len(BUILD_STAGES)
    assert all(s.weight == pytest.approx(share) for s in progress.stages)
    assert progress.percent == pytest.approx(100 * share, abs=0.1)


def test_rule_progress_names_the_specs_still_in_the_loop(tmp_path):
    """Verify the Studio can show which rules are being worked on right now, by id.

    id: TST-PROGRESS-012
    Given: A run whose behaviour_specs stage is running three specs
    When: The progress is asked for before the first is settled, after the first, and after the last
    Then: The waiting ids are all three, then the two still open, then none
    """
    specs = [BusinessSpec(spec_id=f"SPEC-00{i}", title=f"Rule {i}", description="d", given_when_then="Given a When b Then c",
                          target_aggregate="Match", kind=SpecKind.BEHAVIOR.value) for i in (1, 2, 3)]
    seen = []

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        handle = stage_begin("behaviour_specs", owns=())

        def execute(batch, done):
            for spec in batch:
                seen.append(current_progress().rules.waiting)
                done(spec, {"success": True, "status": "FULFILLED"})

        run_behaviour_specs(specs, execute, report=lambda rules: handle.note("rules", asdict(rules)))
        after = current_progress().rules.waiting

    assert seen[0] == ["SPEC-001", "SPEC-002", "SPEC-003"]
    assert seen[1] == ["SPEC-002", "SPEC-003"]
    assert after == []


def test_the_app_is_ready_once_everything_that_builds_it_has_ended(tmp_path, monkeypatch):
    """Verify the checks made on the finished app are not part of the wait: the bar is full and the app is
    reported ready while they run.

    id: TST-PROGRESS-013
    Given: An earlier build in which the checks took as long as everything else together
    When: A kickstart has ended every building stage but one, then that one too, then begun its first check
    Then: It is not ready and the bar is not full; then it is ready at 100 percent with the check still pending;
          then it is still ready, still building, and the check is listed as running
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    _finished_build(str(tmp_path / "runs"), {name: 10.0 for name in STAGE_LABELS})

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        for name in list(CONTRACT_FRONT) + [DRAFT_STAGE] + BUILD_STAGES[:-1]:
            stage_begin(name).ok()
        last = stage_begin(BUILD_STAGES[-1])
        before = current_progress()
        last.fail("no answer")
        built = current_progress()
        stage_begin(FINAL_CHECKS[0])
        checking = current_progress()

    assert before.ready is False and before.percent < 100
    assert built.ready is True and built.percent == 100.0 and built.building is True
    assert checking.ready is True and checking.final_checks[0].status == "running"
    assert sum(s.weight for s in checking.stages) == pytest.approx(1.0)


def test_a_build_lists_only_the_opening_it_runs(tmp_path, monkeypatch):
    """Verify the stages of the opening a build does not run are not part of its road: they would never end, and
    the app would never be reported ready.

    id: TST-PROGRESS-014
    Given: An earlier build in which every stage took as long as any other
    When: A kickstart that opened with the product contract has ended every other building stage
    Then: The stages of the other opening are not listed; the bar is full and the app is ready
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    _finished_build(str(tmp_path / "runs"), {name: 10.0 for name in STAGE_LABELS})

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)):
        for name in list(CONTRACT_FRONT) + [DRAFT_STAGE] + BUILD_STAGES:
            stage_begin(name).ok()
        progress = current_progress()

    assert [s.name for s in progress.opening] == list(CONTRACT_FRONT) + [DRAFT_STAGE]
    assert progress.percent == 100.0 and progress.ready is True
    assert sum(s.weight for s in progress.stages) == pytest.approx(1.0)


def _contract(progress):
    return next(s for s in progress.opening if s.name == "contract")


def test_a_long_stage_says_which_part_of_its_work_it_is_in(tmp_path, monkeypatch):
    """Verify the one long opening stage reads as a row of steps to someone waiting: the steps before the last are
    over with a margin before the stage usually ends, and the last one holds until it does.

    id: TST-PROGRESS-015
    Given: An earlier build whose contract stage took 100 seconds
    When: The contract has just begun, has run for the share of its usual time the phases are done by, has run far
          longer than usual, and has ended
    Then: It names its phases and is in the first, then the last, still the last, and then past them all
    """
    phases = [label for label, _ in STAGE_PHASES["contract"]]
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))
    _finished_build(str(tmp_path / "runs"), {name: 0.0 for name in STAGE_LABELS} | {"contract": 100.0})

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        handle = stage_begin("contract")
        began = run.started + run.stages[0].record["t_offset_s"]
        first = _contract(current_progress(now=began + 0.5))
        again = _contract(current_progress(now=began + 0.5))
        margin = _contract(current_progress(now=began + 100.0 * PHASES_DONE_BY + 0.5))
        overdue = _contract(current_progress(now=began + 10_000.0))
        handle.ok()
        ended = _contract(current_progress())

    last = len(phases) - 1
    assert len(phases) > 2 and first.phases == phases and PHASES_DONE_BY < 1
    assert (first.phase, again.phase, margin.phase, overdue.phase, ended.phase) == (0, 0, last, last, len(phases))


def test_phases_differ_in_length_and_from_build_to_build():
    """Verify the steps do not tick like a clock: a phase given more length takes longer, and no two builds pace
    them alike, while one build always paces them the same.

    id: TST-PROGRESS-016
    Given: Three phases, the second given four times the length of the others, in a stage that usually takes 100 s
    When: Their ends are asked for in one build twice, and in many other builds
    Then: The ends rise to the share of the usual time the phases are done by; the second phase is the longest in
          every build; each phase's share stays within the jitter of its given one; the builds do not agree
    """
    lengths = [1.0, 4.0, 1.0]
    builds = [phase_ends(lengths, 100.0, f"run-{i}") for i in range(50)]
    low, high = 1 - PHASE_JITTER, 1 + PHASE_JITTER

    assert phase_ends(lengths, 100.0, "run-0") == builds[0]
    assert len({tuple(ends) for ends in builds}) == len(builds)
    for ends in builds:
        took = [end - start for start, end in zip([0.0] + ends, ends)]
        assert ends == sorted(ends) and ends[-1] == pytest.approx(100.0 * PHASES_DONE_BY)
        assert took[1] == max(took)
        for given, real in zip(lengths, took):
            assert given * low / (sum(lengths) * high) <= real / sum(took) <= given * high / (sum(lengths) * low)


def test_phases_move_on_a_fresh_install_too(tmp_path, monkeypatch):
    """Verify the phases do not stand still when no recorded build says how long the stage takes.

    id: TST-PROGRESS-017
    Given: No recorded builds
    When: The contract has been in the making for half a second, and for a minute
    Then: It is in its first phase, then in its last
    """
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(tmp_path / "runs"))

    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        stage_begin("contract")
        began = run.started + run.stages[0].record["t_offset_s"]
        early = _contract(current_progress(now=began + 0.5))
        later = _contract(current_progress(now=began + 60.0))

    assert early.phase == 0 and later.phase == len(later.phases) - 1


def test_the_wait_after_the_first_draft_is_timed_from_the_draft(tmp_path):
    """Verify the Studio can time the bar from the moment the app came on screen, not from the pitch.

    id: TST-PROGRESS-018
    Given: A kickstart whose opening is running, and then one whose skeleton is written
    When: The progress is asked for, the second time 20 seconds after the skeleton ended
    Then: No time since the draft is reported before there is one; afterwards it is 20 seconds
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        stage_begin("contract")
        before = current_progress(now=run.started + 30.0)
        stage_begin(DRAFT_STAGE).ok()
        record = run.stages[-1].record
        after = current_progress(now=run.started + record["t_offset_s"] + record["duration_s"] + 20.0)

    assert before.since_draft_s == 0.0 and before.draft_ready is False
    assert after.since_draft_s == pytest.approx(20.0, abs=0.1)
