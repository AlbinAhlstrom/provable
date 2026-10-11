"""
The first tests of a class's rules, written in one answer.

Each rule used to get a writer of its own, which thought before it wrote: sixteen calls side by side for a deck of
sixteen, three quarters of their output hidden thinking, and the slowest of them (about half a minute) held up the
code. What they thought about was what the rule left open: which state to arrange, and what exactly holds afterwards.

The product contract now decides that (ADR-011): a rule starts from a situation written once with its values, is one
action with the value of every parameter, and ends in values. Turning such a rule into a test is transcription, so one
writer does it for every rule of a class at once and without thinking (`STAGE` is among the provider's
`unthinking_stages`): one builder per situation, one test function per rule, named after the rule's id.

The answer is then cut up by rule (`split_by_rule`), because everything after it works rule by rule: each rule's test
is a file of its own, passed through the RED gate, locked by its hash and judged alone (`service_layer/tdd_batch.py`).
A rule whose test the gate refuses, or that the answer left out, goes to a writer of its own with the refusal: the one
regeneration the retry policy allows (`tdd_machine.run_red_phase`).
"""

import ast
import re
from typing import Dict, List

from onboarding.router_engine import BusinessSpec
from pipeline_trace import traced

STAGE = "first_tests"
TIMEOUT_S = 180.0  # one answer holds every test of a class: among the largest answers of a build


def function_name(spec_id: str) -> str:
    """What the names of a rule's test functions start with."""
    return "test_" + re.sub(r"[^a-z0-9]+", "_", spec_id.lower()).strip("_")


def _source_of(node: ast.stmt, lines: List[str]) -> str:
    first = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
    return "\n".join(lines[first - 1:node.end_lineno])


def split_by_rule(module_source: str, spec_ids: List[str]) -> Dict[str, str]:
    """One test module per rule: everything the answer's tests share (imports, constants, builders, helpers) and the
    test functions named after that rule. A rule the answer holds no test for gets an empty module; a test function
    named after no rule is in none. An answer that is not Python is given to every rule whole, so that the gate's
    refusal says what is wrong with it."""
    try:
        tree = ast.parse(module_source)
    except SyntaxError:
        return {spec_id: module_source for spec_id in spec_ids}
    lines = module_source.splitlines()
    names = {spec_id: function_name(spec_id) for spec_id in spec_ids}
    shared: List[str] = []
    own: Dict[str, List[str]] = {spec_id: [] for spec_id in spec_ids}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            owners = [spec_id for spec_id, name in names.items() if node.name == name or node.name.startswith(name + "_")]
            if owners:  # the longest name is the one meant: test_spec_0021_... is SPEC-0021's, not SPEC-002's
                own[max(owners, key=lambda spec_id: len(names[spec_id]))].append(_source_of(node, lines))
        else:
            shared.append(_source_of(node, lines))
    return {spec_id: "\n\n\n".join(shared + tests) + "\n" if tests else "" for spec_id, tests in own.items()}


def _situations(specs: List[BusinessSpec]) -> str:
    seen: List[str] = []
    for spec in specs:
        if spec.situation and spec.situation not in seen:
            seen.append(spec.situation)
    return "\n".join(f"- {situation}" for situation in seen) or "(none: each rule's Given says the state it starts from)"


def _rules(specs: List[BusinessSpec]) -> str:
    return "\n".join(f"- `{function_name(spec.spec_id)}` · {spec.title}: {spec.given_when_then}"
                     + (" (states a limit)" if spec.is_mathematical_boundary else "") for spec in specs)


@traced("tdd.first_tests")
def write_first_tests(specs: List[BusinessSpec], class_source: str, module_name: str, class_name: str,
                      interface_contract: str = "", existing_tests: str = "") -> Dict[str, str]:
    """Has one writer write the first test of every spec of one class, and returns each spec's test module by spec
    id. A provider error raises with its reason; it is never retried."""
    import agent_orchestrator
    from service_layer.tdd_machine import summarize_class_api

    prompt = agent_orchestrator.load_prompt("first_tests.md", {
        "module_name": module_name,
        "target_class_name": class_name,
        "class_api": summarize_class_api(class_source),
        "interface_contract": interface_contract or "(none: no interface method has been promised for this class)",
        "existing_tests": existing_tests or "(none yet: these are the first tests for this class)",
        "situations": _situations(specs),
        "rules": _rules(specs),
    })
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, timeout_s=TIMEOUT_S)
    if not raw or not raw.strip():
        raise RuntimeError(f"Writing the first tests of {class_name} failed: "
                           f"{agent_orchestrator.LAST_LLM_ERROR or 'the LLM returned an empty response'}")
    match = re.search(r"```(?:python)?\s*\n(.*?)```", raw, re.DOTALL)
    return split_by_rule((match.group(1) if match else raw).strip() + "\n", [spec.spec_id for spec in specs])
