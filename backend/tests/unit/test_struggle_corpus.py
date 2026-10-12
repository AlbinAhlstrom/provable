"""Unit tests for the struggle corpus (backend/struggle_corpus.py): where recorded runs got stuck, grouped."""

import json

import struggle_corpus


def _record(seq, step, kind="step", thread="MainThread", chain=(), output=None, error=None):
    record = {"seq": seq, "step": step, "kind": kind, "thread": thread, "caller_chain": list(chain), "input": {}}
    if error is None:
        record["output"] = output
    else:
        record["error"] = error
    return record


def _write_run(root, run_id, records, stages=(), kind="kickstart", label="a booking page", finished=True,
               commit="abc123", model="m-1"):
    folder = root / run_id
    (folder / "trace").mkdir(parents=True)
    meta = {"id": run_id, "kind": kind, "label": label, "started_at": "2030-01-31 09:30:00",
            "git": {"commit": commit}, "llm": {"model": model}}
    (folder / "run.json").write_text(json.dumps(meta), encoding="utf-8")
    for record in records:
        name = f"{record['seq']:03d}_{record['step']}.json"
        (folder / "trace" / name).write_text(json.dumps(record), encoding="utf-8")
    if finished:
        (folder / "summary.json").write_text(json.dumps({"status": "degraded", "stages": list(stages)}),
                                             encoding="utf-8")
    return folder


_REJECTED = {"status": "REJECTED_TAUTOLOGY", "approved": False, "reason": "Test passed before logic was implemented."}
_APPROVED = {"status": "APPROVED_RED", "approved": True, "reason": "Test fails for the right reason."}


def test_a_rejected_gate_is_a_struggle_and_an_approved_one_is_only_a_check(tmp_path):
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [
        _record(1, "llm.red_test_generation", kind="llm", thread="red_0", output="test source"),
        _record(2, "tdd.red_gate", thread="red_0", output=_REJECTED),
        _record(3, "tdd.red_gate", thread="red_1", output=_APPROVED),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert run.checks["tdd.red_gate"] == 2
    assert [(s.step, s.signal, s.reason) for s in run.struggles] == [
        ("tdd.red_gate", "REJECTED_TAUTOLOGY", "Test passed before logic was implemented.")]
    assert run.struggles[0].trace_file == "002_tdd.red_gate.json"


def test_a_struggle_names_the_llm_call_that_came_before_it_on_its_thread(tmp_path):
    # The answer under judgement is the last one given on the same thread, not one a parallel worker gave later.
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [
        _record(1, "llm.red_test_generation", kind="llm", thread="red_0", output="test source"),
        _record(2, "llm.page_test_generation", kind="llm", thread="page_0", output="page test"),
        _record(3, "tdd.red_gate", thread="red_0", output=_REJECTED),
        _record(4, "page_test.run", thread="page_0",
                output={"status": "fail", "reason": "AssertionError: Locator expected to be visible",
                        "evidence": "", "control_not_found": False}),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert {s.step: s.nearest_llm for s in run.struggles} == {
        "tdd.red_gate": "llm.red_test_generation", "page_test.run": "llm.page_test_generation"}


def test_an_answer_judged_on_a_worker_thread_is_found_through_the_step_they_share(tmp_path):
    # One answer holds the tests of a whole class; a pool then gates each test on its own thread, while a stage
    # running alongside gets an answer of its own in between.
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [
        _record(1, "llm.first_tests", kind="llm", chain=("domain.round", "tdd.first_tests"), output="tests"),
        _record(2, "llm.page_writer", kind="llm", thread="page", chain=("presentation",), output="page"),
        _record(3, "tdd.red_gate", thread="red_0", chain=("domain.round", "tdd.execute_together"), output=_REJECTED),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert run.struggles[0].nearest_llm == "llm.first_tests"


def test_a_page_test_that_found_no_control_has_its_own_signal(tmp_path):
    folder = _write_run(tmp_path, "20300131-093000_rule_tests_a", [
        _record(1, "page_test.run", output={"status": "pass", "reason": None, "control_not_found": False}),
        _record(2, "page_test.run", output={"status": "fail", "reason": "TimeoutError: Locator.click",
                                            "control_not_found": True}),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert [s.signal for s in run.struggles] == ["control_not_found"]


def test_an_exception_is_counted_where_it_was_raised_not_at_each_step_it_passed_through(tmp_path):
    error = "NoClassInAnswer: the response did not contain a definition of class Order"
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [
        _record(1, "tdd.green_synthesize", chain=("domain.round", "tdd.green_together"), error=error),
        _record(2, "tdd.green_together", chain=("domain.round",), error=error),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert [(s.step, s.signal) for s in run.struggles] == [("tdd.green_synthesize", "NoClassInAnswer")]


def test_a_failed_stage_is_a_struggle_and_a_skipped_one_is_not(tmp_path):
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [], stages=[
        {"name": "contract", "status": "ok", "error": None},
        {"name": "behaviour_specs", "status": "failed", "error": "SPEC-006: SyntaxError in the generated test"},
        {"name": "seed_data", "status": "skipped", "error": "no entity is shown to the audience"},
    ])

    run = struggle_corpus.read_run(str(folder))

    assert [(s.step, s.signal, s.reason) for s in run.struggles] == [
        ("stage.behaviour_specs", "failed", "SPEC-006: SyntaxError in the generated test")]
    assert run.checks == {"stage.contract": 1, "stage.behaviour_specs": 1}


def test_every_problem_a_review_could_not_repair_is_its_own_struggle(tmp_path):
    folder = _write_run(tmp_path, "20300131-093000_kickstart_a", [
        _record(1, "visual.review", output={"verdict": "unrepaired", "error": None,
                                            "not_repaired": ["The heading is cut off.", "The list is empty."]}),
        _record(2, "engine.spec_review", output={"success": True, "conflicts": [
            {"specs": ["SPEC-001", "SPEC-002"], "reason": "Both set the status."}]}),
    ])

    run = struggle_corpus.read_run(str(folder))

    assert [(s.step, s.signal, s.reason) for s in run.struggles] == [
        ("visual.review", "not_repaired", "The heading is cut off."),
        ("visual.review", "not_repaired", "The list is empty."),
        ("engine.spec_review", "conflict", "Both set the status."),
    ]


def test_build_groups_struggles_across_runs_and_keeps_the_rate(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    _write_run(runs, "20300131-093000_kickstart_a", [
        _record(1, "llm.red_test_generation", kind="llm", output="test"),
        _record(2, "tdd.red_gate", output=_REJECTED),
        _record(3, "tdd.red_gate", output=_APPROVED),
    ], label="a booking page", commit="aaa", model="m-1")
    _write_run(runs, "20300201-093000_kickstart_b", [
        _record(1, "llm.red_test_generation", kind="llm", output="test"),
        _record(2, "tdd.red_gate", output=_REJECTED),
    ], label="a card game", commit="bbb", model="m-2")

    corpus = struggle_corpus.build(str(runs), str(corpus_path))

    entry = corpus["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]
    assert entry["occurrences"] == 2
    assert corpus["checks"]["tdd.red_gate"] == 3
    assert entry["runs"] == ["20300131-093000_kickstart_a", "20300201-093000_kickstart_b"]
    assert entry["labels"] == ["a booking page", "a card game"]
    assert entry["models"] == ["m-1", "m-2"]
    assert entry["nearest_llm"] == {"llm.red_test_generation": 2}
    assert (entry["first_seen"], entry["last_seen"], entry["last_commit"]) == (
        "20300131-093000_kickstart_a", "20300201-093000_kickstart_b", "bbb")
    assert entry["examples"][-1] == {"run": "20300201-093000_kickstart_b", "trace": "002_tdd.red_gate.json",
                                     "reason": "Test passed before logic was implemented."}
    assert json.loads(corpus_path.read_text(encoding="utf-8")) == corpus


def test_a_run_is_counted_once_and_keeps_its_count_after_its_folder_is_pruned(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    folder = _write_run(runs, "20300131-093000_kickstart_a", [_record(1, "tdd.red_gate", output=_REJECTED)])
    struggle_corpus.build(str(runs), str(corpus_path))

    again = struggle_corpus.build(str(runs), str(corpus_path))
    assert again["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]["occurrences"] == 1

    for path in sorted(folder.rglob("*"), reverse=True):
        path.rmdir() if path.is_dir() else path.unlink()
    folder.rmdir()
    pruned = struggle_corpus.build(str(runs), str(corpus_path))
    assert pruned["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]["occurrences"] == 1
    assert pruned["runs"] == ["20300131-093000_kickstart_a"]


def test_a_run_still_in_progress_is_left_for_the_next_build(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    folder = _write_run(runs, "20300131-093000_kickstart_a", [_record(1, "tdd.red_gate", output=_REJECTED)],
                        finished=False)

    assert struggle_corpus.build(str(runs), str(corpus_path))["entries"] == {}

    (folder / "summary.json").write_text(json.dumps({"status": "ok", "stages": []}), encoding="utf-8")
    assert list(struggle_corpus.build(str(runs), str(corpus_path))["entries"]) == ["tdd.red_gate/REJECTED_TAUTOLOGY"]


def test_a_review_written_into_the_corpus_survives_the_next_build(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    _write_run(runs, "20300131-093000_kickstart_a", [_record(1, "tdd.red_gate", output=_REJECTED)])
    corpus = struggle_corpus.build(str(runs), str(corpus_path))
    entry = corpus["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]
    assert entry["review"] == {"status": "candidate", "cause": "", "knowledge": ""}

    entry["review"] = {"status": "reviewed", "cause": "the test asserts the starting state", "knowledge": "..."}
    corpus_path.write_text(json.dumps(corpus), encoding="utf-8")
    _write_run(runs, "20300201-093000_kickstart_b", [_record(1, "tdd.red_gate", output=_REJECTED)])

    rebuilt = struggle_corpus.build(str(runs), str(corpus_path))["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]
    assert rebuilt["occurrences"] == 2
    assert rebuilt["review"]["cause"] == "the test asserts the starting state"


def test_an_entry_keeps_its_latest_examples_only_with_long_reasons_cut(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    long_reason = dict(_REJECTED, reason="x" * 2000)
    _write_run(runs, "20300131-093000_kickstart_a",
               [_record(n, "tdd.red_gate", output=long_reason) for n in range(1, 6)])

    entry = struggle_corpus.build(str(runs), str(corpus_path))["entries"]["tdd.red_gate/REJECTED_TAUTOLOGY"]

    assert entry["occurrences"] == 5
    assert [e["trace"] for e in entry["examples"]] == [f"00{n}_tdd.red_gate.json" for n in (3, 4, 5)]
    assert all(len(e["reason"]) == struggle_corpus.REASON_LIMIT for e in entry["examples"])


def test_the_report_lists_the_most_frequent_struggle_first_with_its_rate(tmp_path):
    runs, corpus_path = tmp_path / "runs", tmp_path / "corpus.json"
    _write_run(runs, "20300131-093000_kickstart_a", [
        _record(1, "tdd.red_gate", output=_REJECTED),
        _record(2, "tdd.red_gate", output=_APPROVED),
        _record(3, "tdd.red_gate", output=_REJECTED),
        _record(4, "tdd.red_gate", output=_APPROVED),
        _record(5, "visual.review", output={"verdict": "unrepaired", "error": None, "not_repaired": ["Cut off."]}),
    ])

    lines = struggle_corpus.report_lines(struggle_corpus.build(str(runs), str(corpus_path)))

    assert "1 run" in lines[0]
    assert lines[1].split()[:4] == ["2", "of", "4", "tdd.red_gate/REJECTED_TAUTOLOGY"]
    assert lines[2].split()[:4] == ["1", "of", "1", "visual.review/not_repaired"]
