"""
Diagnosing a red rule: where the fault lies is found before anything is changed.

A rule's page test can fail for four reasons, and each is corrected somewhere else:

- `page`: the app did what the rule says and the page did not show it, or the page never asked. The page is
  changed (`rule_fix.py`).
- `logic`: the page asked, and the action as it is written did something else than the plan says. The record's
  class is changed through the test-first loop (`logic_fix.py`).
- `rules`: two rules about the action cannot both hold. No code keeps them all, so nothing is changed and the
  rules are named.
- `test`: the test does not arrange, do or expect what the rule says. Nothing is changed; the test is to be
  written again.

A rule of the page alone (it names no action) is the page's by definition, and nothing is asked. Otherwise it is one
call, shown what a writer of the page never saw: what the app held when the test ended, the action as it is written,
what the plan says it does, the rule's test of the method alone and the other rules about the action. The answer is
a verdict on where to look, never a change.

Before the verdict the answer works each rule about the action through against the plan and writes that down
(`checked`): the closing condition of the action counted on the rule's own records, what the action leaves behind,
and whether the rule states that. Asked for the verdict alone, the small and the middle model both overlooked a rule
that says a record goes on although the action, done from the rule's situation, completes it; made to count, both
found it. A rule that does not hold against the plan is the fault, by code, whatever else was found.
"""

import ast
import os
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.product_contract import ProductContract
from pipeline_trace import traced

STAGE = "rule_diagnosis"
PAGE, LOGIC, RULES, TEST = "page", "logic", "rules", "test"
FAULTS = (PAGE, LOGIC, RULES, TEST)
_TEXT = {"type": "string"}
DIAGNOSIS_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        # each rule about the action worked through against the plan, before the verdict is given
        "checked": {"type": "array", "items": {
            "type": "object",
            "properties": {"rule": _TEXT, "closing": _TEXT, "leaves": _TEXT, "holds": {"type": "boolean"}},
            "required": ["rule", "closing", "leaves", "holds"]}},
        "fault": {"type": "string", "enum": list(FAULTS)}, "why": _TEXT},
    "required": ["checked", "fault", "why"],
}
_NONE = "(none)"


class NoDiagnosis(RuntimeError):
    """The model gave no diagnosis (a provider or parse error). Never retried."""


@dataclass
class Diagnosis:
    fault: str
    why: str = ""
    rules: List[str] = field(default_factory=list)  # titles of the rules that cannot hold together


@dataclass
class Case:
    """What the diagnosis is shown of one red rule."""
    title: str
    rule: str
    situation: str = ""
    test: str = ""            # the page test that failed
    reason: str = ""
    evidence: str = ""
    seen: str = ""            # what the page sent the app and what the app held when the test ended
    action: str = ""          # the action by name and parameters, and what the plan says it does
    method: str = ""          # the action as it is written, with the methods it calls
    unit_test: str = ""       # the rule's test of the method alone
    unit_test_said: str = ""
    others: List[str] = field(default_factory=list)  # the other rules about the action, one line each


def method_with_helpers(class_source: str, name: str) -> str:
    """The method `name` of a class with every method of the class it reaches through `self`, each whole, in the
    order the class has them. Empty when the class has no such method."""
    try:
        cls = next(n for n in ast.walk(ast.parse(class_source)) if isinstance(n, ast.ClassDef))
    except (SyntaxError, StopIteration):
        return ""
    methods = {n.name: n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    if name not in methods:
        return ""
    reached, waiting = set(), [name]
    while waiting:
        current = waiting.pop()
        if current in reached:
            continue
        reached.add(current)
        waiting.extend(node.attr for node in ast.walk(methods[current])
                       if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                       and node.value.id in ("self", "cls") and node.attr in methods)
    lines = class_source.splitlines()

    def source_of(node: ast.AST) -> str:
        first = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        return "\n".join(lines[first - 1:node.end_lineno])

    return "\n\n".join(source_of(node) for node in cls.body if getattr(node, "name", None) in reached)


def _read(path: str) -> str:
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def _ran(path: str) -> str:
    """What the rule's unit test says when it is run now."""
    from service_layer.tdd_machine import run_isolated_pytest, summarize_pytest_failure
    result = run_isolated_pytest(path, cwd=os.path.dirname(os.path.dirname(os.path.dirname(path))))
    return "It passes." if result.get("exit_code") == 0 else "It fails:\n" + summarize_pytest_failure(result, limit=1200)


def case_of(rule: Dict[str, Any], stored: Dict[str, Any], contract: Optional[ProductContract], workspace_dir: str,
            run_unit_test: Callable[[str], str] = _ran) -> Case:
    """Puts together what the diagnosis is shown, from the rule, its stored page test, the contract the app was built
    from (None for an app built without one) and the app's files."""
    from onboarding import logic_fix, page_tests
    from onboarding.cst_isolator import extract_class_cst

    name, owner = str(rule.get("action") or ""), str(rule.get("target_aggregate") or rule.get("target") or "")
    planned = next((a for a in (contract.actions if contract else []) if a.name == name), None)
    action = f"`{name}({', '.join(planned.params)})`: {planned.does}" if planned else f"`{name}`"
    others = [f"- {other.title}: Given {contract.situation_of(other.given) or other.given}, When {other.when}, "
              f"Then {other.then}"
              for other in (contract.rules if contract else [])
              if other.action == name and other.title != rule.get("title")]

    module = _read(logic_fix.domain_path(rule, workspace_dir))
    unit_path = logic_fix.unit_test_path(rule, workspace_dir)
    unit_test = _read(unit_path)
    return Case(
        title=str(rule.get("title") or ""), rule=page_tests.rule_text(rule), situation=str(rule.get("situation") or ""),
        test=str(stored.get("source") or ""), reason=str(stored.get("reason") or ""),
        evidence=str(stored.get("evidence") or ""), seen=str(stored.get("seen") or ""), action=action,
        method=method_with_helpers(extract_class_cst(module, owner) or "", name) if module else "",
        unit_test=unit_test, unit_test_said=run_unit_test(unit_path) if unit_test else "", others=others)


@traced("rule_diagnosis.diagnose")
def diagnose(case: Case) -> Diagnosis:
    """Has the model say where the fault of a red rule lies. One call; raises NoDiagnosis when none was given."""
    import agent_orchestrator
    prompt = agent_orchestrator.load_prompt("rule_diagnosis.md", {
        "title": case.title, "rule": case.rule, "situation": case.situation or _NONE, "action": case.action,
        "test": case.test, "reason": case.reason, "evidence": case.evidence,
        "seen": case.seen or "(not noted: the test ran before the app's side was recorded)",
        "method": case.method or "# the action has no method in the record's class",
        "unit_test": case.unit_test or "# the rule has no test of the method alone",
        "unit_test_said": case.unit_test_said or _NONE,
        "others": "\n".join(case.others) or "(none: this is the only rule about the action)",
    })
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, json_mode=True, json_schema=DIAGNOSIS_SCHEMA)
    if not raw or not raw.strip():
        raise NoDiagnosis(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
    try:
        said = agent_orchestrator.extract_json_object(raw)
    except ValueError as err:
        raise NoDiagnosis(f"the diagnosis is not valid JSON: {err}") from None
    fault = str(said.get("fault") or "").strip().lower()
    if fault not in FAULTS:
        raise NoDiagnosis(f"the diagnosis names a fault that is none of {', '.join(FAULTS)}: {fault or 'nothing'}")
    # a rule that was worked through and does not hold against the plan settles it, whatever else was found
    against = [str(check.get("rule") or "").strip() for check in said.get("checked") or []
               if isinstance(check, dict) and check.get("holds") is False and str(check.get("rule") or "").strip()]
    return Diagnosis(fault=RULES if against else fault, why=" ".join(str(said.get("why") or "").split()), rules=against)


def diagnose_rule(rule: Dict[str, Any], stored: Dict[str, Any], contract: Optional[ProductContract], workspace_dir: str,
                  ask: Callable[[Case], Diagnosis] = diagnose) -> Diagnosis:
    """Where the fault of a red rule lies. A rule that names no action is of the page alone: nothing is asked."""
    if not str(rule.get("action") or "").strip():
        return Diagnosis(PAGE, "The rule is about the page alone: nothing is sent to the app.")
    return ask(case_of(rule, stored, contract, workspace_dir))
