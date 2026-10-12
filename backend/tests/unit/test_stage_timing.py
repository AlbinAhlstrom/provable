"""How long each stage of a build usually takes, learned from the recorded runs (backend/onboarding/stage_timing.py).

The Studio's progress bar gives every stage a length in proportion to its usual share of a build. Nothing is tuned by
hand for this: the run recorder keeps a summary of every finished run, and the averages are read from those.
"""
import json
import os

import pytest

from onboarding.stage_timing import average_durations, stage_weights


def _summary(root, run_id, stages, kind="kickstart", status="ok"):
    os.makedirs(os.path.join(root, run_id))
    with open(os.path.join(root, run_id, "summary.json"), "w", encoding="utf-8") as f:
        json.dump({"id": run_id, "kind": kind, "status": status,
                   "stages": [{"name": name, "status": outcome, "duration_s": seconds} for name, outcome, seconds in stages]}, f)


def test_a_stage_takes_the_average_of_what_it_took_in_the_finished_builds(tmp_path):
    """Verify the usual duration of a stage is its mean over the recorded builds.

    id: TST-TIMING-001
    Given: Two finished kickstarts in which the page took 60 and 40 seconds
    When: The average durations are asked for
    Then: The page takes 50 seconds
    """
    root = str(tmp_path)
    _summary(root, "a", [("intent", "ok", 4.0), ("presentation", "ok", 60.0)])
    _summary(root, "b", [("intent", "ok", 2.0), ("presentation", "ok", 40.0)])

    assert average_durations(root) == {"intent": 3.0, "presentation": 50.0}


def test_only_builds_that_went_well_teach_the_durations(tmp_path):
    """Verify runs that say nothing about a normal build are left out.

    id: TST-TIMING-002
    Given: A good kickstart, a kickstart that ended in an error, a page rebuild, a folder with no summary and a
           summary that cannot be read
    When: The average durations are asked for
    Then: Only the good kickstart counts
    """
    root = str(tmp_path)
    _summary(root, "good", [("intent", "ok", 3.0)])
    _summary(root, "crashed", [("intent", "failed", 90.0)], status="error")
    _summary(root, "page", [("intent", "ok", 50.0)], kind="page")
    os.makedirs(os.path.join(root, "still-running"))
    os.makedirs(os.path.join(root, "torn"))
    with open(os.path.join(root, "torn", "summary.json"), "w", encoding="utf-8") as f:
        f.write("{")

    assert average_durations(root) == {"intent": 3.0}


def test_a_skipped_stage_counts_as_the_time_it_took(tmp_path):
    """Verify a stage that is usually skipped is known to take next to nothing, instead of being unknown.

    id: TST-TIMING-003
    Given: A finished kickstart whose seed data stage was skipped at once
    When: The average durations are asked for
    Then: The seed data stage has its near-zero duration
    """
    root = str(tmp_path)
    _summary(root, "a", [("seed_data", "skipped", 0.01), ("presentation", "ok", 60.0)])

    assert average_durations(root)["seed_data"] == 0.01


def test_no_recorded_builds_means_no_durations(tmp_path):
    """Verify a fresh install has nothing to learn from, and says so.

    id: TST-TIMING-004
    Given: No runs folder, and an empty one
    When: The average durations are asked for
    Then: Both give none
    """
    assert average_durations(str(tmp_path / "missing")) == {}
    assert average_durations(str(tmp_path)) == {}


def test_a_stage_weighs_its_share_of_the_summed_stage_time():
    """Verify weights are shares of the work, so stages that run side by side each keep their own length.

    id: TST-TIMING-005
    Given: Stages that usually take 10, 30 and 60 seconds
    When: Their weights are asked for
    Then: They weigh 0.1, 0.3 and 0.6
    """
    weights = stage_weights(["intent", "ux_plan", "presentation"], {"intent": 10.0, "ux_plan": 30.0, "presentation": 60.0})

    assert weights == pytest.approx({"intent": 0.1, "ux_plan": 0.3, "presentation": 0.6})


def test_without_history_every_stage_weighs_the_same():
    """Verify the bar still works on a fresh install: equal steps until there is something to learn from.

    id: TST-TIMING-006
    Given: Four stages and no known durations
    When: Their weights are asked for
    Then: Each weighs a quarter
    """
    assert stage_weights(["a", "b", "c", "d"], {}) == pytest.approx({"a": 0.25, "b": 0.25, "c": 0.25, "d": 0.25})


def test_a_stage_never_seen_before_weighs_as_an_average_stage():
    """Verify a stage added to the pipeline since the last recorded build gets a plain share, not none.

    id: TST-TIMING-007
    Given: Two stages that usually take 10 and 30 seconds, and a third with no history
    When: Their weights are asked for
    Then: The new stage is treated as taking their mean, 20 seconds, and the weights still sum to one
    """
    weights = stage_weights(["a", "b", "new"], {"a": 10.0, "b": 30.0})

    assert weights == pytest.approx({"a": 10 / 60, "b": 30 / 60, "new": 20 / 60})
