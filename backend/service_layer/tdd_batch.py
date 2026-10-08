"""
TDD batch: a deck's rules are written together.

The single-spec loop (`tdd_machine.execute_spec_tdd_loop`) is right for one rule added to an app that exists. A
kickstart has the whole deck at once, and one spec after another made the rules most of its duration: every rule
waited for the test call and the code call of the rule before it, and each code call rewrote a class the previous
one had just rewritten.

Here the same gates are passed in two steps:

1. RED, side by side. Every spec gets its test through the RED phase the single loop uses (`run_red_phase`: lint,
   RED gate, hollow check, one regeneration with the verdict fed back). The tests are written against the class as
   it is before any of them is implemented, so none depends on another's code.
2. GREEN, once per class. One code answer implements every rule of the class whose test was approved. The whole
   `tests/unit` folder is then run and each spec is judged by its own test file. Tests still failing are fed back
   for the one retry the policy allows (.claude/rules/pipeline.md).

What is kept afterwards:

- The answer that leaves the fewest of the batch's tests failing, among those that break no earlier verified test.
  When both answers break one, the class goes back to what it was and every spec of the batch fails by name.
- A spec whose test still fails moves to `tests/pending` with the reason. Unlike the single loop, the code written
  for it cannot be taken out of an answer that also carries the other rules: it stays, and every test left in
  `tests/unit` passes.
- The hash lock holds for every test of the batch: the code writer cannot have changed any of them.
- A test that neither code answer could meet goes back to its writer once (`reconsider_test`), with the failure and
  its own test: a test can expect the wrong thing (a check that is not one), and then a correct class fails it.
  The writer either corrects the expectation or returns the test unchanged. A corrected test must pass on the class
  as kept and fail on the hollow class (`hollow_check.py`); it then stands as the rule's test. This is the test
  writer's one regeneration: a test the RED gate already sent back is not reconsidered, and no code is written
  after it.

Classes are implemented one after another (the regression run covers the whole folder); the tests of classes still
waiting are ignored in that run.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import pipeline_trace
from onboarding.cst_isolator import FragmentError, extract_class_cst, merge_module_fragment, module_import_lines
from onboarding.router_engine import BusinessSpec
from pipeline_trace import traced
from service_layer import tdd_machine
from service_layer.tdd_machine import DomainTarget, RedOutcome

RED_WORKERS = 8
FEEDBACK_LIMIT = 6000  # characters of failing-test output shown to the code writer on the retry

RECONSIDER_EVIDENCE = 2500
RECONSIDER = """Two implementations of the class could not make this test pass, while every other test of the class passes.

Your test:
```python
{test}
```

How it fails:
```
{evidence}
```

Either the implementation lacks the rule, or the test expects the wrong thing for the state it arranges. Work out from
the product's rules, item by item, what the correct result is for exactly that state. If the test expected the wrong
thing, write it again with a correct expectation, still testing this rule in a situation where it applies. If the test
was right, return it exactly as it is."""

Approved = Tuple[BusinessSpec, RedOutcome]


def rules_spec(class_name: str, specs: List[BusinessSpec]) -> BusinessSpec:
    """The one spec the code writer is given for every rule of a class."""
    scenarios = " ".join(f"({n}) {s.title}: {s.given_when_then}" for n, s in enumerate(specs, 1))
    return BusinessSpec(
        spec_id=f"RULES-{class_name.upper()}",
        title=f"{len(specs)} rules of {class_name}, each with its own frozen test",
        description=f"Every rule below holds for {class_name} at the same time.",
        given_when_then=scenarios,
        target_aggregate=class_name,
        spec_type="DOMAIN_INVARIANT",
    )


def _tests_block(batch: List[Approved]) -> str:
    return "\n".join(f"# tests/unit/{os.path.basename(red.test_file_path)}\n{red.test_code.strip()}\n" for _, red in batch)


def _first_failures(batch: List[Approved]) -> str:
    share = max(400, FEEDBACK_LIMIT // len(batch))
    return "\n".join(f"# {os.path.basename(red.test_file_path)}\n"
                     f"{tdd_machine.summarize_pytest_failure(red.result, limit=share)}" for _, red in batch)


def _failing_spec_result(spec: BusinessSpec, red: RedOutcome, attempts: List[Dict[str, Any]], error: str,
                         workspace_dir: str, phase: str = "DEAD_END") -> Dict[str, Any]:
    return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "phase": phase, "spec_id": spec.spec_id,
            "error": error, "red_attempts": red.attempts, "test_source": red.test_code, "attempts": attempts,
            "rolled_back": True, "pending_test": tdd_machine._quarantine_test(red.test_file_path, workspace_dir)}


@traced("tdd.green_together")
def implement_together(batch: List[Approved], target: DomainTarget, workspace_dir: str, existing_tests: str,
                       waiting: Set[str]) -> Dict[str, Dict[str, Any]]:
    """One code answer for every approved test of one class, and one retry with the tests it left failing.
    `waiting` holds the test files of classes not implemented yet: they fail by design and are not counted."""
    with open(target.domain_file, "r", encoding="utf-8") as f:
        domain_before = f.read()
    spec = rules_spec(target.class_name, [s for s, _ in batch])
    own = {os.path.basename(red.test_file_path) for _, red in batch}
    attempts: List[Dict[str, Any]] = []
    kept: Optional[Tuple[str, Set[str], Dict[str, Any]]] = None   # (source, the batch's failing tests, pytest result)
    reason = ""
    failure = _first_failures(batch)

    def restore(source: str) -> None:
        with open(target.domain_file, "w", encoding="utf-8") as f:
            f.write(source)

    try:
        for attempt in (1, 2):
            with open(target.domain_file, "r", encoding="utf-8") as f:
                domain_source = f.read()
            fragment = tdd_machine.synthesize_green_class_implementation(
                extracted_class=extract_class_cst(domain_source, target.class_name) or "",
                target_class_name=target.class_name, spec=spec, failure_output=failure,
                test_source=_tests_block(batch), module_imports=module_import_lines(domain_source),
                existing_tests=existing_tests)
            try:
                merged = merge_module_fragment(domain_source, target.class_name, fragment)
            except FragmentError as err:
                reason, evidence = f"The answer could not be merged into the class: {err}", str(err)
            else:
                restore(merged)
                for _, red in batch:
                    tdd_machine.verify_test_file_integrity(red.test_file_path, red.test_hash)
                run = tdd_machine.run_isolated_pytest(target.tests_dir, cwd=workspace_dir,
                                                      timeout_seconds=tdd_machine.REGRESSION_TIMEOUT_S)
                if run.get("timed_out"):
                    # Not a verdict on the code: the suite never answered, so there is nothing to feed back
                    restore(domain_before)
                    error = (f"The regression suite (tests/unit) did not finish within "
                             f"{tdd_machine.REGRESSION_TIMEOUT_S} seconds, so the change could not be verified.")
                    attempts.append({"attempt": attempt, "approved": False, "reason": error})
                    return {s.spec_id: _failing_spec_result(s, red, attempts, error, workspace_dir, "REGRESSION_GATE")
                            for s, red in batch}
                failed = set(tdd_machine._failed_test_files(run)) - waiting
                if run["exit_code"] != 0 and not tdd_machine._failed_test_files(run):
                    failed = set(own)  # pytest itself stopped (the module does not import): no test was verified
                still, earlier = failed & own, sorted(failed - own)
                evidence = tdd_machine.summarize_pytest_failure(run, limit=FEEDBACK_LIMIT)
                if earlier:
                    reason = (f"Regression: your change makes earlier tests fail again: {', '.join(earlier)}. "
                              f"Keep every existing behavior.")
                    restore(domain_source)
                else:
                    reason = f"These frozen tests still fail: {', '.join(sorted(still))}." if still else ""
                    if kept is None or len(still) <= len(kept[1]):
                        kept = (merged, still, run)
                    restore(kept[0])
            attempts.append({"attempt": attempt, "approved": not reason, "reason": reason or "All tests passed cleanly."})
            if not reason:
                break
            failure = f"The previous GREEN attempt was rejected: {reason}\n{evidence}"
    except BaseException:
        restore(domain_before)
        for _, red in batch:
            tdd_machine._quarantine_test(red.test_file_path, workspace_dir)
        raise

    results: Dict[str, Dict[str, Any]] = {}
    if kept is None:
        restore(domain_before)
        return {s.spec_id: _failing_spec_result(s, red, attempts, reason, workspace_dir) for s, red in batch}
    _, still, run = kept
    for s, red in batch:
        name = os.path.basename(red.test_file_path)
        if name in still:
            evidence = "\n".join(str((t.get("call") or {}).get("longrepr") or "")
                                 for t in (run.get("report") or {}).get("tests", [])
                                 if name in str(t.get("nodeid", "")) and (t.get("call") or {}).get("outcome") == "failed")
            why = tdd_machine._headline(evidence) if evidence.strip() else ""
            results[s.spec_id] = _failing_spec_result(
                s, red, attempts, f"Test assertions failed in GREEN phase{': ' + why if why else '.'}", workspace_dir)
            results[s.spec_id]["rolled_back"] = False  # the answer also carries the rules that passed, so it stays
            results[s.spec_id]["failure_evidence"] = evidence[-RECONSIDER_EVIDENCE:]
        else:
            results[s.spec_id] = {
                "success": True, "status": "FULFILLED", "phase": "COMMITTED", "spec_id": s.spec_id,
                "test_file": red.test_file_path, "red_eval": red.evaluation,
                "green_eval": {"status": "APPROVED_GREEN", "approved": True, "reason": "All tests passed cleanly."},
                "red_attempts": red.attempts, "test_source": red.test_code, "attempts": attempts}
    return results


@traced("tdd.reconsider_test")
def reconsider_test(spec: BusinessSpec, red: RedOutcome, failed: Dict[str, Any], target: DomainTarget,
                    workspace_dir: str, existing_tests: str, action_manifest: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """The test writer's one regeneration, spent on a test no code answer could meet. Returns the spec's result:
    fulfilled by a corrected test that the kept class passes and the hollow class fails, else `failed` with what
    the reconsideration came to."""
    def stays(reason: str, attempt: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {**failed, "error": f"{failed['error']} {reason}", "red_attempts": red.attempts + ([attempt] if attempt else [])}

    with open(target.domain_file, "r", encoding="utf-8") as f:
        current_class = extract_class_cst(f.read(), target.class_name) or ""
    test_code = tdd_machine.generate_red_test(
        spec, current_class, target.module_name, target.class_name,
        rejection_feedback=RECONSIDER.format(test=red.test_code.strip(), evidence=failed.get("failure_evidence") or failed["error"]),
        existing_tests=existing_tests,
        interface_contract=tdd_machine.format_interface_contract(action_manifest, target.class_name))
    if test_code.strip() == red.test_code.strip():
        return stays("Its writer, shown the failure, stands by the test.")
    lint_ok, lint_reason = tdd_machine.lint_red_test(test_code, require_both_sides=bool(spec.is_mathematical_boundary))
    if not lint_ok:
        return stays("The reconsidered test was refused.", {"attempt": 2, "approved": False, "reason": lint_reason})

    with open(red.test_file_path, "w", encoding="utf-8") as f:
        f.write(test_code)
    run = tdd_machine.run_isolated_pytest(red.test_file_path, cwd=workspace_dir)
    if run["exit_code"] == 0 and tdd_machine.fails_without_behaviour(
            red.test_file_path, workspace_dir, target.domain_file, target.class_name,
            run=tdd_machine.run_isolated_pytest, judge=tdd_machine.evaluate_red_gate_result):
        if failed.get("pending_test") and os.path.exists(failed["pending_test"]):
            os.remove(failed["pending_test"])  # replaced by the corrected test
        evaluation = {"status": "ALREADY_SATISFIED", "approved": True,
                      "reason": "The first test expected the wrong thing. The corrected test passes on the class as "
                                "written and fails once the class's methods do nothing."}
        return {"success": True, "status": "FULFILLED", "phase": "COMMITTED", "spec_id": spec.spec_id,
                "test_file": red.test_file_path, "red_eval": evaluation, "test_source": test_code,
                "red_attempts": red.attempts + [{"attempt": 2, "approved": True, "reason": evaluation["reason"]}],
                "attempts": failed.get("attempts", []), "already_satisfied": True, "reconsidered": True}
    os.remove(red.test_file_path)
    reason = ("The reconsidered test fails too." if run["exit_code"] != 0
              else "The reconsidered test passes even when the class's methods do nothing, so it asserts no behaviour.")
    return stays(reason, {"attempt": 2, "approved": False,
                          "reason": f"{reason} {tdd_machine._headline(tdd_machine.summarize_pytest_failure(run))}".strip()})


@traced("tdd.execute_together")
def execute_specs_together(
    specs: List[BusinessSpec],
    workspace_dir: str,
    action_manifest: Optional[Dict[str, Any]] = None,
    on_result: Optional[Callable[[BusinessSpec, Dict[str, Any]], None]] = None,
) -> Dict[str, Dict[str, Any]]:
    """Runs every spec through RED side by side, then GREEN once per class. Returns each spec's result by spec id,
    in the shape the single loop returns; `on_result` is told each one, in deck order within its class, from the
    calling thread."""
    targets = {s.spec_id: tdd_machine.locate_domain_target(s, workspace_dir) for s in specs}
    # What each test writer is shown: the verified tests from before this batch, read before any new one is written
    earlier_tests = {t.domain_file: tdd_machine.collect_existing_tests(t.tests_dir, exclude="", module_name=t.module_name)
                     for t in targets.values()}

    def red(spec: BusinessSpec) -> Any:
        target = targets[spec.spec_id]
        try:
            return tdd_machine.run_red_phase(spec, target, workspace_dir, earlier_tests[target.domain_file], action_manifest)
        except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
            return err

    with ThreadPoolExecutor(max_workers=RED_WORKERS, thread_name_prefix="red") as pool:
        reds = list(pool.map(pipeline_trace.bind_context(red), specs))

    results: Dict[str, Dict[str, Any]] = {}

    def settle(spec: BusinessSpec, result: Dict[str, Any]) -> None:
        results[spec.spec_id] = result
        if on_result is not None:
            on_result(spec, result)

    by_class: Dict[str, List[Approved]] = {}
    for spec, outcome in zip(specs, reds):
        if isinstance(outcome, Exception):
            settle(spec, {"success": False, "status": "ERROR", "phase": "RED_GEN", "spec_id": spec.spec_id,
                          "error": f"{type(outcome).__name__}: {outcome}"})
            continue
        settled = tdd_machine.red_dead_end(spec, outcome, workspace_dir)
        if settled is not None:
            settle(spec, settled)
        else:
            by_class.setdefault(targets[spec.spec_id].domain_file, []).append((spec, outcome))

    waiting = {os.path.basename(red.test_file_path) for batch in by_class.values() for _, red in batch}
    for domain_file, batch in by_class.items():
        waiting -= {os.path.basename(red.test_file_path) for _, red in batch}
        try:
            done = implement_together(batch, targets[batch[0][0].spec_id], workspace_dir, earlier_tests[domain_file], waiting)
        except Exception as err:  # a provider error or a tampered test: the class is back as it was, nothing is retried
            done = {s.spec_id: {"success": False, "status": "ERROR", "phase": "GREEN_GEN", "spec_id": s.spec_id,
                                "error": f"{type(err).__name__}: {err}", "red_attempts": red.attempts,
                                "test_source": red.test_code, "rolled_back": True} for s, red in batch}
        # A test neither answer could meet, and never sent back before, goes to its writer once
        doubted = [(spec, red) for spec, red in batch
                   if "failure_evidence" in done[spec.spec_id] and len(red.attempts) == 1]

        def reconsider(pair: Approved) -> Dict[str, Any]:
            spec, red = pair
            try:
                return reconsider_test(spec, red, done[spec.spec_id], targets[spec.spec_id], workspace_dir,
                                       earlier_tests[domain_file], action_manifest)
            except Exception as err:  # a provider error: the spec stays failed, with this beside its reason
                return {**done[spec.spec_id], "error": f"{done[spec.spec_id]['error']} Reconsidering its test failed: "
                                                       f"{type(err).__name__}: {err}"}

        if doubted:
            with ThreadPoolExecutor(max_workers=RED_WORKERS, thread_name_prefix="reconsider") as pool:
                for (spec, _), result in zip(doubted, pool.map(pipeline_trace.bind_context(reconsider), doubted)):
                    done[spec.spec_id] = result
        for spec, _ in batch:
            settle(spec, done[spec.spec_id])
    return results
