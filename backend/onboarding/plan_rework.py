"""
A plan whose review names rules is sent back once, for those rules alone, before anything is built from it.

The review of the rule deck (`spec_review.py`) finds rules that cannot hold: against what the plan says their action
does, or against each other. Built as written, such a rule gets a green test of the class alone and surfaces later
as a page test no fix can turn green. So the rules the review names go back to the writer of the plan, with what the
review found, before the build starts.

- Only the named rules are rewritten, and the situations they need are added. The actions decide what the app does
  and are not the rework's to change; nor is a situation other rules start from. The plan is some seven thousand
  tokens and a rule under a hundred, so this is a tenth of writing the plan again, and nothing else of it can drift.
- What comes back is checked by code: only named rules, only new situations, and every rewritten rule the records
  obey starts from a situation of the plan. Anything else fails by name (`ReworkError`).
- Once. The verdict of a verifying step buys one more attempt (.claude/rules/pipeline.md); the reworked rules are
  reviewed by the build's own review stage, which reports what is left and changes nothing.
"""

import copy
from typing import Any, Dict, List, Set

import agent_orchestrator
from onboarding import product_contract as pc
from pipeline_trace import traced

STAGE = "plan_rework"
REWORK_TIMEOUT_S = 90.0
CLAUSES = ("given", "when", "then", "sees", "plain")   # what of a rule is rewritten; its title, action and feature stay

_TEXT = {"type": "string"}
REWORK_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "situations": {"type": "array", "items": _TEXT},
        "rules": {"type": "array", "minItems": 1, "items": {   # a review named at least one; an empty list builds them unchanged
            "type": "object", "properties": {key: _TEXT for key in ("title", *CLAUSES)},
            "required": ["title", *CLAUSES]}},
    },
    "required": ["situations", "rules"],
}


class ReworkError(RuntimeError):
    """The rework of a plan's rules was not delivered, or was not what was asked for; the message says which."""


def named_rules(contract: pc.ProductContract, conflicts: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """The rules a review named, by title, each with what the review found about it."""
    by_id = {spec.spec_id: rule.title for spec, rule in zip(contract.specs(), contract.rules)}
    named: Dict[str, List[str]] = {}
    for conflict in conflicts:
        for spec_id in conflict.get("specs") or []:
            if spec_id in by_id:
                named.setdefault(by_id[spec_id], []).append(str(conflict.get("reason") or ""))
    return named


def _block(contract: pc.ProductContract, named: Dict[str, List[str]]) -> str:
    lines = []
    for rule in contract.rules:
        if rule.title not in named:
            continue
        about = f" (about the action `{rule.action}`)" if rule.action else " (a rule of the page alone)"
        lines.append(f"- **{rule.title}**{about}: Given {rule.given}, When {rule.when}, Then {rule.then or rule.sees}")
        lines.extend(f"  What the review found: {reason}" for reason in named[rule.title])
    return "\n".join(lines)


def _name(situation: str) -> str:
    name, equals, holds = str(situation).partition("=")
    return name.strip() if equals and holds.strip() else ""


def applied(contract: pc.ProductContract, answer: Dict[str, Any], named: Set[str]) -> pc.ProductContract:
    """The plan with an answer's rules and situations in it. Raises ReworkError for an answer that rewrites nothing,
    touches a rule the review did not name or a situation the plan already has, or leaves a rule without one."""
    rewritten = {str(rule.get("title") or ""): rule for rule in answer.get("rules") or [] if isinstance(rule, dict)}
    if not rewritten:
        raise ReworkError("the answer rewrote no rule")
    unnamed = sorted(set(rewritten) - named)
    if unnamed:
        raise ReworkError(f"the answer rewrote a rule that was not named by the review: {', '.join(unnamed)}")
    source = copy.deepcopy(contract.source)
    known = {_name(entry) for entry in contract.situations}
    for entry in answer.get("situations") or []:
        if not _name(entry):
            raise ReworkError(f"a situation is not written as `name = what it holds`: {entry}")
        if _name(entry) in known:
            raise ReworkError(f"the answer changed a situation other rules start from: {_name(entry)}")
        known.add(_name(entry))
        source.setdefault("situations", []).append(str(entry))
    for rule in source["rules"]:
        if rule.get("title") in rewritten:
            rule.update({key: str(rewritten[rule["title"]].get(key) or "") for key in CLAUSES})
    reworked = pc.ProductContract.from_dict(source)
    for rule in reworked.rules:
        if rule.title in rewritten and rule.action and not reworked.situation_of(rule.given):
            raise ReworkError(f'the rule "{rule.title}" starts from no situation of the plan: {rule.given}')
    return reworked


@traced("plan.rework")
def rework_rules(contract: pc.ProductContract, conflicts: List[Dict[str, Any]]) -> pc.ProductContract:
    """Has the rules a review named written again, with one LLM call, and answers with the plan that holds them.
    Raises ReworkError on any failure; nothing is retried."""
    named = named_rules(contract, conflicts)
    if not named:
        raise ReworkError("the review named no rule of the plan")
    prompt = agent_orchestrator.load_prompt("plan_rework.md", {
        "contract": pc.to_json(contract), "named_rules": _block(contract, named)})
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, json_mode=True, json_schema=REWORK_SCHEMA,
                                         timeout_s=REWORK_TIMEOUT_S)
    if not raw or not raw.strip():
        raise ReworkError(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
    try:
        answer = agent_orchestrator.extract_json_object(raw)
    except Exception as exc:
        raise ReworkError(f"the rework is not valid JSON: {exc}") from exc
    return applied(contract, answer, set(named))
