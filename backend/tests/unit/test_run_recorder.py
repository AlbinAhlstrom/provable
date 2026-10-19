"""Unit tests for the per-run recorder (backend/run_recorder.py): one folder per pipeline run."""

import json
import os

import pytest

import pipeline_trace
import run_recorder
from pipeline_trace import traced, traced_llm


@pytest.fixture
def runs_root(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(root))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    monkeypatch.delenv("PROVABLE_TRACE_DIR", raising=False)
    return root


@pytest.fixture
def workspace(tmp_path):
    ws = tmp_path / "ws"
    (ws / "src").mkdir(parents=True)
    (ws / "src" / "App.tsx").write_text("old", encoding="utf-8")
    return ws


@traced("unit.step")
def _step(x):
    return x + 1


@traced_llm
def _llm(prompt, stage="general"):
    pipeline_trace.record_llm_meta(model="m-1", prompt_tokens=10, completion_tokens=5, finish_reason="stop")
    return "answer"


def _only_run(root):
    runs = [p for p in root.iterdir() if p.is_dir()]
    assert len(runs) == 1
    return runs[0]


def test_each_run_gets_its_own_folder_with_metadata_and_trace(runs_root, workspace):
    """Verify a recorded run writes run.json, a numbered trace and summary.json in a folder of its own.

    id: TST-RR-001
    Given: Two pipeline runs in one process
    When: Each executes traced steps
    Then: Each has its own folder, trace numbering restarts, and run.json names the code version and model
    """
    for label in ("first pitch", "second pitch"):
        with run_recorder.recorded_run("kickstart", label, workspace_dir=str(workspace)):
            _step(1)
            _llm("hello", stage="demo")

    runs = sorted(p for p in runs_root.iterdir() if p.is_dir())
    assert len(runs) == 2
    for run in runs:
        meta = json.loads((run / "run.json").read_text(encoding="utf-8"))
        assert meta["kind"] == "kickstart" and "pitch" in meta["label"]
        assert "commit" in meta["git"] and "model" in meta["llm"]
        names = sorted(os.listdir(run / "trace"))
        assert names[0].startswith("001_") and len(names) == 2
        assert (run / "summary.json").exists()
    assert (runs_root / "LATEST").read_text(encoding="utf-8").strip() == runs[-1].name
    assert pipeline_trace.trace_dir() == ""  # tracing stops when the run ends


def test_stages_record_status_files_changed_and_degrade_the_run(runs_root, workspace):
    """Verify stage outcomes, the files each stage wrote, and the degraded verdict.

    id: TST-RR-002
    Given: A run whose first stage rewrites App.tsx and whose second stage reports failure
    When: The run ends
    Then: summary.json lists both stages, attributes App.tsx to the first, and marks the run degraded
    """
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        with run_recorder.stage("shell"):
            (workspace / "src" / "App.tsx").write_text("new shell", encoding="utf-8")
            (workspace / "src" / "Extra.tsx").write_text("x", encoding="utf-8")
        presentation = run_recorder.stage_begin("presentation")
        presentation.fail("the answer has no App.tsx")
        run_recorder.stage_begin("styling").skip("presentation failed")

    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in summary["stages"]}
    assert by_name["shell"]["status"] == "ok"
    assert {f["path"]: f["change"] for f in by_name["shell"]["files_changed"]} == {
        "src/App.tsx": "modified", "src/Extra.tsx": "added"}
    assert by_name["presentation"]["status"] == "failed" and "no App.tsx" in by_name["presentation"]["error"]
    assert by_name["styling"]["status"] == "skipped"
    assert summary["status"] == "degraded"
    assert summary["failed_stages"] == ["presentation"]
    assert summary["provenance"]["src/App.tsx"] == "shell"


def test_an_exception_in_a_stage_is_recorded_and_reraised(runs_root, workspace):
    """Verify errors are never swallowed by the recorder.

    id: TST-RR-003
    Given: A stage that raises
    When: The run unwinds
    Then: The exception propagates and the run is marked as an error with the reason
    """
    with pytest.raises(RuntimeError, match="boom"):
        with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
            with run_recorder.stage("decompose"):
                raise RuntimeError("boom")
    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "error" and "boom" in summary["error"]
    assert summary["stages"][0]["status"] == "failed"


def test_llm_calls_are_aggregated_with_tokens_and_errors(runs_root, workspace):
    """Verify LLM metadata lands in the trace and in the summary totals.

    id: TST-RR-004
    Given: One successful LLM call
    When: The run ends
    Then: The call file carries the model and token counts and the summary totals them per stage
    """
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        _llm("hello", stage="demo")
    run = _only_run(runs_root)
    call = json.loads((run / "trace" / os.listdir(run / "trace")[0]).read_text(encoding="utf-8"))
    assert call["meta"]["model"] == "m-1" and call["meta"]["prompt_tokens"] == 10
    llm = json.loads((run / "summary.json").read_text(encoding="utf-8"))["llm"]
    assert llm["calls"] == 1 and llm["prompt_tokens"] == 10 and llm["completion_tokens"] == 5
    assert llm["by_stage"]["demo"]["calls"] == 1


def test_the_workspace_source_is_snapshotted_with_the_run(runs_root, workspace):
    """Verify the generated app survives the next run overwriting the workspace.

    id: TST-RR-005
    Given: A run that writes a view
    When: The run ends
    Then: The run folder holds a copy of src/ (without node_modules)
    """
    (workspace / "node_modules").mkdir()
    (workspace / "node_modules" / "junk.js").write_text("x", encoding="utf-8")
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        (workspace / "src" / "View.tsx").write_text("view", encoding="utf-8")
    snap = _only_run(runs_root) / "workspace"
    assert (snap / "src" / "View.tsx").read_text(encoding="utf-8") == "view"
    assert not (snap / "node_modules").exists()


def test_nested_runs_join_the_outer_run_and_stages_are_inert_outside_a_run(runs_root, workspace):
    """Verify a run started inside a run reuses it, and stage handles are harmless with no run.

    id: TST-RR-006
    Given: A recorded function called inside another recorded run, and a stage used with no run
    When: They execute
    Then: Only one folder exists and the loose stage records nothing and raises nothing
    """
    @run_recorder.recorded("spec", label="spec_id")
    def inner(spec_id):
        return {"success": True}

    with run_recorder.recorded_run("kickstart", "outer", workspace_dir=str(workspace)):
        inner("SPEC-1")
    _only_run(runs_root)

    with run_recorder.stage("loose") as handle:
        handle.fail("nobody is listening")


def test_decorator_derives_the_verdict_from_the_returned_result(runs_root, workspace):
    """Verify result dicts with stage_failures or success=False degrade the run and are summarised.

    id: TST-RR-007
    Given: A recorded function returning stage_failures and timings
    When: It returns
    Then: summary.json is degraded and carries the failures and timings
    """
    @run_recorder.recorded("kickstart", label="pitch")
    def go(pitch, workspace_dir=None):
        return {"success": True, "stage_failures": [{"stage": "presentation", "error": "x"}],
                "timing_breakdown": {"total": 1.5}, "created_files": ["a", "b"]}

    go("a babysitter site", workspace_dir=str(workspace))
    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    assert summary["status"] == "degraded"
    assert summary["result"]["stage_failures"] == [{"stage": "presentation", "error": "x"}]
    assert summary["result"]["timing_breakdown"] == {"total": 1.5}


def test_recording_can_be_switched_off(monkeypatch, runs_root, workspace):
    """Verify PROVABLE_RECORD_RUNS=0 writes nothing.

    id: TST-RR-008
    Given: Recording disabled
    When: A run executes
    Then: No folder is created
    """
    monkeypatch.setenv("PROVABLE_RECORD_RUNS", "0")
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        _step(1)
    assert not runs_root.exists()


def test_old_runs_are_pruned(monkeypatch, runs_root, workspace):
    """Verify only the newest PROVABLE_RUNS_KEEP runs are kept.

    id: TST-RR-009
    Given: Retention of 2 and three runs
    When: The third ends
    Then: Two run folders remain
    """
    monkeypatch.setenv("PROVABLE_RUNS_KEEP", "2")
    for i in range(3):
        with run_recorder.recorded_run("kickstart", f"p{i}", workspace_dir=str(workspace)):
            pass
    assert len([p for p in runs_root.iterdir() if p.is_dir()]) == 2


def test_a_kickstart_records_its_stages_in_a_run_folder(runs_root, tmp_path):
    """Verify the real kickstart service leaves a run with its stages, trace and workspace copy.

    id: TST-RR-010
    Given: An offline kickstart (fake unit of work, no LLM)
    When: kickstart_domain_and_scaffold returns
    Then: One run folder holds the intent, decomposition and skeleton stages, the files the skeleton wrote and a trace
    """
    from service_layer import services
    from service_layer.unit_of_work import FakeUnitOfWork

    result = services.kickstart_domain_and_scaffold(pitch="A pallet tracking system with storage zones",
                                                    uow=FakeUnitOfWork(), workspace_dir=str(tmp_path))
    run = _only_run(runs_root)
    assert result["run_id"] == run.name
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    names = [s["name"] for s in summary["stages"]]
    assert names[:3] == ["intent", "expansion", "decomposition"] and "skeleton" in names
    skeleton = next(s for s in summary["stages"] if s["name"] == "skeleton")
    assert skeleton["files_changed"], "the skeleton stage should be credited with the files it wrote"
    assert summary["result"]["success"] is True and summary["kind"] == "kickstart"
    assert list((run / "trace").glob("*svc.kickstart_and_scaffold.json"))
    assert (run / "workspace" / "src").is_dir()


def test_trace_report_shows_the_verdict_compares_runs_and_prints_one_step(runs_root, workspace):
    """Verify scripts/trace_report.py reads recorded runs: report, --list, --compare, --full.

    id: TST-RR-011
    Given: A healthy run and a later degraded one
    When: The report tool runs against them
    Then: It prints each verdict, the failing stage's reason, the status change between runs and a step's full payload
    """
    import subprocess
    import sys

    for fail in (False, True):
        with run_recorder.recorded_run("kickstart", "pitch", workspace_dir=str(workspace)):
            with run_recorder.stage("presentation") as st:
                _llm("the prompt", stage="presentation_projection_synthesis")
                if fail:
                    st.fail("the answer has no App.tsx")
    first, second = sorted(p.name for p in runs_root.iterdir() if p.is_dir())

    def report(*args):
        script = os.path.join(os.path.dirname(__file__), "..", "..", "..", "scripts", "trace_report.py")
        res = subprocess.run([sys.executable, script, *args], capture_output=True, text=True, encoding="utf-8",
                             env={**os.environ, "PROVABLE_RUNS_DIR": str(runs_root)})
        assert res.returncode == 0, res.stderr
        return res.stdout

    latest = report()
    assert "DEGRADED" in latest and "the answer has no App.tsx" in latest and "llm.presentation_projection_synthesis" in latest
    assert "OK" in report(first)
    assert "ok" in report("--list") and "degraded" in report("--list")
    comparison = report("--compare", first, second)
    assert "ok" in comparison and "degraded" in comparison and "<-- changed" in comparison
    assert "the prompt" in report(second, "--full", "1")


def test_a_stage_left_open_by_an_exception_is_marked_failed(runs_root, workspace):
    """Verify the stage an exception interrupted is reported as failed, not ok.

    id: TST-RR-012
    Given: A stage begun with stage_begin whose body raises before it is closed
    When: The run unwinds
    Then: That stage is failed with the exception text
    """
    with pytest.raises(ValueError):
        with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
            run_recorder.stage_begin("done").ok()
            run_recorder.stage_begin("interrupted")
            raise ValueError("no key")
    stages = {s["name"]: s for s in json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))["stages"]}
    assert stages["done"]["status"] == "ok"
    assert stages["interrupted"]["status"] == "failed" and "no key" in stages["interrupted"]["error"]


def test_stages_record_when_they_started_and_how_large_the_files_became(runs_root, workspace):
    """Verify the summary can show a timeline and a stage's effect on file size (styling grew a view by 172 lines unseen).

    id: TST-RR-013
    Given: A stage that writes a three-line file, then a stage that grows it to five lines
    When: The run ends
    Then: Each stage has an offset from the run start, and the file's line count and delta are recorded
    """
    target = workspace / "src" / "View.tsx"
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        with run_recorder.stage("presentation"):
            target.write_text("a\nb\nc\n", encoding="utf-8")
        with run_recorder.stage("styling"):
            target.write_text("a\nb\nc\nd\ne\n", encoding="utf-8")
    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    by_name = {s["name"]: s for s in summary["stages"]}
    assert by_name["presentation"]["t_offset_s"] <= by_name["styling"]["t_offset_s"]
    assert by_name["presentation"]["files_changed"] == [{"path": "src/View.tsx", "change": "added", "lines": 3}]
    assert by_name["styling"]["files_changed"] == [{"path": "src/View.tsx", "change": "modified", "lines": 5, "delta": 2}]


def test_concurrent_stages_are_credited_only_with_their_own_files(runs_root, workspace):
    """Verify running stages in parallel does not blur which stage wrote a file.

    id: TST-RR-014
    Given: A seed stage that owns src/seed.json, open while a presentation stage writes src/App.tsx
    When: Both files change before either stage closes
    Then: Each stage lists only its own file, and the provenance map agrees
    """
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        seed = run_recorder.stage_begin("seed_data", owns=("src/seed.json",))
        presentation = run_recorder.stage_begin("presentation")
        (workspace / "src" / "seed.json").write_text("{}", encoding="utf-8")
        (workspace / "src" / "App.tsx").write_text("new", encoding="utf-8")
        presentation.ok()
        seed.ok()
    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    by_name = {s["name"]: [f["path"] for f in s["files_changed"]] for s in summary["stages"]}
    assert by_name == {"seed_data": ["src/seed.json"], "presentation": ["src/App.tsx"]}
    assert summary["provenance"] == {"src/seed.json": "seed_data", "src/App.tsx": "presentation"}


def test_the_summary_accounts_for_the_whole_wall_time(runs_root, workspace):
    """Verify time spent outside every stage is reported instead of silently missing from the breakdown.

    id: TST-RR-015
    Given: A run with one short stage
    When: The run ends
    Then: The timeline holds the time covered by stages and the remainder, and they add up to the duration
    """
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(workspace)):
        with run_recorder.stage("only"):
            pass
    summary = json.loads((_only_run(runs_root) / "summary.json").read_text(encoding="utf-8"))
    timeline = summary["timeline"]
    assert timeline["in_stages_s"] >= 0 and timeline["outside_stages_s"] >= 0
    assert abs(timeline["in_stages_s"] + timeline["outside_stages_s"] - summary["duration_s"]) < 0.05


def test_a_run_names_the_model_of_each_stage_that_has_its_own(runs_root, workspace, monkeypatch):
    """Verify the record of a run names every stage that runs on another model than the run's own, whether the
    provider gives it one or a setting moves it: a run recorded the small model alone while its contract was written
    by the middle one, and the report pointed at the wrong model.

    id: TST-RR-STAGE-MODELS
    Given: The Anthropic provider, which gives some stages a model of their own, and a setting moving one more
    When: A run is recorded
    Then: run.json names the run's model, and each such stage with its model
    """
    import llm_provider
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("LLM_MODEL_PRODUCT_CONTRACT", raising=False)
    monkeypatch.setenv("LLM_MODEL_FIRST_TESTS", "m-moved")
    with run_recorder.recorded_run("kickstart", "pitch", workspace_dir=str(workspace)):
        _step(1)

    llm = json.loads((_only_run(runs_root) / "run.json").read_text(encoding="utf-8"))["llm"]
    provider = llm_provider.PROVIDERS["anthropic"]
    assert llm["model"] == provider.model
    assert llm["stage_models"] == {**provider.stage_models, "first_tests": "m-moved"}
