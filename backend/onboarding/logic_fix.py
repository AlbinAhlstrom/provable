"""
Fixing a red rule whose fault is in what the app does: the record's class is changed, not the page.

The diagnosis (`rule_diagnosis.py`) found that the page asked for the right action and the action did something else
than the plan says. The class is changed where every change of a class is made, in the test-first loop
(`service_layer/tdd_machine.py`):

- The loop starts from a red test. The rule's unit test was green, or the kickstart would not have kept the class,
  so it arranged something the page test did not. The test writer is therefore shown the page test and what the
  app held when it ended, and writes the rule's unit test again for exactly those records.
- The loop keeps its own gates: the new test is red first, the class passes it, and every other rule's unit test
  still passes.
- Then the page decides (`check`, as for a change of the page): the rule's page test passes and every rule that
  was green still is. Otherwise the class and the rule's unit test are put back as they were.

Nothing is retried here beyond the loop's own single retry (.claude/rules/pipeline.md).
"""

import os
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, Optional

from onboarding import page_tests
from onboarding.router_engine import BusinessSpec
from onboarding.rule_fix import FIXED, NOT_FIXED, Check
from pipeline_trace import traced

Loop = Callable[..., Dict[str, Any]]


def unit_test_path(rule: Dict[str, Any], workspace_dir: str) -> str:
    """Where the rule's test of its class alone is kept."""
    from service_layer.tdd_machine import spec_test_path
    return spec_test_path(SimpleNamespace(spec_id=page_tests.rule_id(rule)), os.path.join(workspace_dir, "tests", "unit"))


def domain_path(rule: Dict[str, Any], workspace_dir: str) -> str:
    """The module of the record the rule is about."""
    from onboarding.skeleton_builder import to_snake_case
    owner = str(rule.get("target_aggregate") or rule.get("target") or "")
    return os.path.join(workspace_dir, "src", "domain", f"{to_snake_case(owner)}.py")


def spec_of(rule: Dict[str, Any], stored: Dict[str, Any]) -> BusinessSpec:
    """The rule as the loop's spec. What the test writer reads of it ends with the page test that failed and what
    the app held, so the unit test starts from the records the fault showed in."""
    shown = (f"{rule.get('description') or rule.get('title') or ''}\n"
             "This rule's test on the app's page failed, and the fault is in the method, not on the page. Arrange the "
             "Given as that test arranged it through the app's API: the same records, with the same value in every "
             "field and in every part of a list. Call the method with the values the page sent. Expect what the rule "
             "states.\n\nThe page test that failed:\n```python\n"
             f"{str(stored.get('source') or '').strip()}\n```\n\n{str(stored.get('seen') or '').strip()}")
    return BusinessSpec(
        spec_id=page_tests.rule_id(rule), title=str(rule.get("title") or ""), description=shown.strip(),
        given_when_then=str(rule.get("given_when_then") or page_tests.rule_text(rule)),
        target_aggregate=str(rule.get("target_aggregate") or rule.get("target") or ""),
        spec_type=str(rule.get("spec_type") or "DOMAIN_INVARIANT"),
        is_mathematical_boundary=bool(rule.get("is_mathematical_boundary", False)),
        priority=str(rule.get("priority") or "High"), situation=str(rule.get("situation") or ""),
        action=str(rule.get("action") or ""))


def _read(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        return f.read()


def _put_back(before: Dict[str, Optional[str]]) -> None:
    for path, source in before.items():
        if source is None:
            if os.path.exists(path):
                os.remove(path)
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(source)


def _attempts(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [{"number": a.get("attempt"), "ok": bool(a.get("approved")), "reason": a.get("reason")}
            for a in result.get("attempts") or []]


@traced("logic_fix.fix")
def fix_logic(rule: Dict[str, Any], stored: Dict[str, Any], workspace_dir: str, manifest: Optional[Dict[str, Any]],
              check: Callable[[], Check], loop: Optional[Loop] = None) -> Dict[str, Any]:
    """Has the test-first loop change the rule's class from the situation its page test failed in, and keeps the
    change only when `check` holds. Answers as `rule_fix.fix` does: status, reason, files, attempts; with `tdd`,
    what the loop said, when the change was kept, and `broke`, the unit test files of other rules its last change
    broke, when it was not."""
    if loop is None:
        from service_layer.tdd_machine import execute_spec_tdd_loop as loop
    paths = [domain_path(rule, workspace_dir), unit_test_path(rule, workspace_dir)]
    before = {path: _read(path) for path in paths}

    def not_fixed(reason: str, attempts: List[Dict[str, Any]], broke: Optional[List[str]] = None) -> Dict[str, Any]:
        _put_back(before)
        return {"status": NOT_FIXED, "reason": reason, "files": [], "attempts": attempts, "broke": list(broke or [])}

    try:
        result = loop(spec_of(rule, stored), workspace_dir, manifest)
    except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
        return not_fixed(f"{type(err).__name__}: {err}", [])
    attempts = _attempts(result)
    if not result.get("success"):
        return not_fixed(str(result.get("error") or result.get("status") or "the test-first loop did not reach green"),
                         attempts, broke=result.get("broke"))
    verdict = check()
    if not verdict.ok:
        return not_fixed(verdict.reason, attempts)
    files = [os.path.relpath(path, workspace_dir).replace(os.sep, "/") for path in paths if os.path.exists(path)]
    return {"status": FIXED, "reason": None, "files": files, "attempts": attempts, "tdd": result}
