"""The Studio can show an app while it is being built (backend/onboarding/build_progress.py).

A kickstart answers only when everything is done, minutes after its page was written. What the run recorder already
knows about the running build (which stages are open, which delivered) is read out as a typed progress report: is the
page there yet, how many rules are active, what is being worked on.
"""
from dataclasses import asdict

from onboarding.build_progress import BuildProgress, current_progress
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


def test_a_running_kickstart_reports_its_stages_in_plain_words(tmp_path):
    """Verify each stage of the running build is listed with its status and a label a visitor can read.

    id: TST-PROGRESS-002
    Given: A kickstart run whose skeleton stage is done and whose presentation stage is open
    When: The progress is asked for
    Then: It is building; both stages are listed in order with their status and a label; the app can be shown as a
          draft, and the page is not ready
    """
    with recorded_run("kickstart", "a pitch", workspace_dir=str(tmp_path)) as run:
        stage_begin("skeleton").ok()
        stage_begin("presentation")
        progress = current_progress()

    assert progress.building is True and progress.run_id == run.id
    assert [(s.name, s.status) for s in progress.stages] == [("skeleton", "ok"), ("presentation", "running")]
    assert all(s.label and s.label != s.name for s in progress.stages)
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
    assert failed.page_ready is False and failed.stages[0].error == "the answer has no App.tsx"


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
    assert data["stages"][0] == {"name": "presentation", "label": data["stages"][0]["label"], "status": "ok", "error": None}
