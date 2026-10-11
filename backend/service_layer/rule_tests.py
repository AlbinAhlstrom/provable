"""
Running a rule's page test (ADR-010): one rule, or every active rule of the deck.

A run changes no code. Its outcome (pass, fail or broken, with the reason, the evidence and the test itself) is
stored on the rule: on its card in the deck, or with the spec when the rule is only in the inbox. The Studio's light
is read from there (`onboarding/spec_test_status.py`).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Tuple

import pipeline_trace
from onboarding import page_tests
from run_recorder import recorded
from service_layer.unit_of_work import AbstractUnitOfWork

# Rules tested at the same time: each has a browser and an API of its own
SIDE_BY_SIDE = 6
Prove = Callable[..., Dict[str, Any]]


def _page_url() -> str:
    from onboarding.server_manager import get_preview_url
    return get_preview_url()


def _workspace() -> str:
    from config_loader import get_workspace_base
    return get_workspace_base()


def _find(state: Any, spec_id: str) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """The rule's card and its stored spec, either of which may be missing."""
    card = next((c for c in (state.rule_cards or []) if c.get("id") == spec_id), None)
    spec = next((s for s in (state.inbox_specs or []) if s.get("spec_id") == spec_id), None)
    return card, spec


def _rule(card: Optional[Dict[str, Any]], spec: Optional[Dict[str, Any]], spec_id: str) -> Dict[str, Any]:
    """The rule as the test writer needs it: the card's clauses are what the person reads, so they come first."""
    rule = {**(spec or {}), **(card or {})}
    rule.pop("page_test", None)
    rule.pop("tdd", None)
    rule["spec_id"] = spec_id
    return rule


def record_page_test(spec_id: str, outcome: Dict[str, Any], uow: AbstractUnitOfWork) -> None:
    """Stores a page test's outcome on the rule, with the time it ran."""
    stored = {**{k: v for k, v in outcome.items() if k != "written"},
              "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    with uow:
        state = uow.kickstart.get()
        card, spec = _find(state, spec_id)
        holder = card if card is not None else spec
        if holder is None:
            return
        holder["page_test"] = stored
        uow.kickstart.save(state)
        uow.commit()


@recorded("rule_test", label="spec_id")
def run_rule_test(spec_id: str, uow: AbstractUnitOfWork, workspace_dir: Optional[str] = None,
                  page_url: Optional[str] = None, prove: Optional[Prove] = None, rewrite: bool = False) -> Dict[str, Any]:
    """Runs one rule's page test and stores what it said. With `rewrite` the stored test is set aside and a new one
    is written first: for a test that is itself wrong."""
    prove = prove or page_tests.prove_rule
    with uow:
        state = uow.kickstart.get()
        card, spec = _find(state, spec_id)
        card, spec = (dict(card) if card else None), (dict(spec) if spec else None)
        plan = page_tests.page_plan(state.business_pitch)
    if card is None and spec is None:
        return {"success": False, "status": "not_found", "reason": f"Rule {spec_id} not found."}
    stored = None if rewrite else (card or {}).get("page_test") or (spec or {}).get("page_test")
    outcome = prove(_rule(card, spec, spec_id), workspace_dir or _workspace(), page_url or _page_url(), stored=stored,
                    plan=plan)
    record_page_test(spec_id, outcome, uow=uow)
    return {"success": outcome["status"] == page_tests.PASS, "spec_id": spec_id, **outcome}


@recorded("rule_fix", label="spec_id")
def fix_rule_test(spec_id: str, uow: AbstractUnitOfWork, workspace_dir: Optional[str] = None, page_url: Optional[str] = None,
                  fixer: Optional[Callable[..., Dict[str, Any]]] = None, prove: Optional[Prove] = None) -> Dict[str, Any]:
    """Has the page changed so that a red rule's test turns green (`onboarding/rule_fix.py`). The rules that are
    green guard the change: it is kept only when they all still are. A kept change is followed by a run of the
    rule's test, so the light that turns green is one that was seen."""
    from onboarding import rule_fix
    fixer = fixer or rule_fix.fix_rule
    workspace_dir, page_url = workspace_dir or _workspace(), page_url or _page_url()
    with uow:
        state = uow.kickstart.get()
        card, spec = _find(state, spec_id)
        card, spec = (dict(card) if card else None), (dict(spec) if spec else None)
        green = {c["id"]: c["page_test"]["source"] for c in (state.rule_cards or [])
                 if c.get("id") != spec_id and c.get("is_active", True)
                 and (c.get("page_test") or {}).get("status") == page_tests.PASS and c["page_test"].get("source")}
    if card is None and spec is None:
        return {"success": False, "status": "not_found", "reason": f"Rule {spec_id} not found."}
    stored = (card or {}).get("page_test") or (spec or {}).get("page_test")
    result = fixer(_rule(card, spec, spec_id), stored, workspace_dir, page_url, green)
    fixed = result["status"] == rule_fix.FIXED
    if fixed:
        run_rule_test(spec_id, uow=uow, workspace_dir=workspace_dir, page_url=page_url, prove=prove)
    return {"success": fixed, "spec_id": spec_id, **result}


@recorded("rule_tests", label="label")
def run_all_rule_tests(uow: AbstractUnitOfWork, workspace_dir: Optional[str] = None, page_url: Optional[str] = None,
                       prove: Optional[Prove] = None, describe: Optional[Callable[..., Any]] = None,
                       label: str = "deck") -> Dict[str, Any]:
    """Runs the page test of every active rule of the deck, several at a time, storing each outcome as it arrives."""
    prove, describe = prove or page_tests.prove_rule, describe or page_tests.describe_app
    workspace_dir, page_url = workspace_dir or _workspace(), page_url or _page_url()
    with uow:
        state = uow.kickstart.get()
        cards = [dict(c) for c in (state.rule_cards or []) if c.get("is_active", True)]
        specs = {s.get("spec_id"): dict(s) for s in (state.inbox_specs or [])}
        plan = page_tests.page_plan(state.business_pitch)
    # read once: every test that has to be written is shown the same app
    app = describe(workspace_dir, page_url, plan=plan)

    def one(card: Dict[str, Any]) -> Dict[str, Any]:
        spec = specs.get(card["id"])
        stored = card.get("page_test") or (spec or {}).get("page_test")
        try:
            return prove(_rule(card, spec, card["id"]), workspace_dir, page_url, stored=stored, app=app)
        except Exception as err:  # this rule could not be judged; the others still are
            reason = f"{type(err).__name__}: {err}"
            return {"status": page_tests.BROKEN, "reason": reason, "evidence": reason,
                    "source": (stored or {}).get("source"), "written_for": page_tests.rule_text(card), "written": 0}

    outcomes: Dict[str, Dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=SIDE_BY_SIDE) as pool:
        waiting = {pool.submit(pipeline_trace.bind_context(one), card): card["id"] for card in cards}
        for done in as_completed(waiting):
            spec_id = waiting[done]
            outcomes[spec_id] = done.result()
            record_page_test(spec_id, outcomes[spec_id], uow=uow)  # one at a time: the deck is stored as a whole
            print(f"[Rules] {spec_id}: {outcomes[spec_id]['status']} {outcomes[spec_id].get('reason') or ''}", flush=True)

    rules: List[Dict[str, Any]] = [
        {"spec_id": c["id"], "title": c.get("title", ""), "status": outcomes[c["id"]]["status"],
         "reason": outcomes[c["id"]].get("reason"), "written": outcomes[c["id"]].get("written", 0)} for c in cards]
    counts = {status: sum(1 for r in rules if r["status"] == status)
              for status in (page_tests.PASS, page_tests.FAIL, page_tests.BROKEN)}
    return {"success": counts[page_tests.FAIL] == 0 and counts[page_tests.BROKEN] == 0, "counts": counts, "rules": rules}
