"""
Running a rule's page test (ADR-010): one rule, or every active rule of the deck.

A run changes no code. Its outcome (pass, fail or broken, with the reason, the evidence and the test itself) is
stored on the rule: on its card in the deck, or with the spec when the rule is only in the inbox. The Studio's light
is read from there (`onboarding/spec_test_status.py`).
"""

import os
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


def record_page_test(spec_id: str, outcome: Dict[str, Any], uow: AbstractUnitOfWork, ran_at: Optional[str] = None) -> None:
    """Stores a page test's outcome on the rule, with the time it ran (now, unless `ran_at` says the run is an
    earlier one that only gains something, such as the cause a diagnosis found)."""
    stored = {**{k: v for k, v in outcome.items() if k != "written"},
              "ran_at": ran_at or datetime.now(timezone.utc).isoformat(timespec="seconds")}
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


def _not_changed(status: str, reason: str) -> Dict[str, Any]:
    return {"status": status, "reason": reason, "files": [], "attempts": []}


@recorded("rule_fix", label="spec_id")
def fix_rule_test(spec_id: str, uow: AbstractUnitOfWork, workspace_dir: Optional[str] = None, page_url: Optional[str] = None,
                  fixer: Optional[Callable[..., Dict[str, Any]]] = None, prove: Optional[Prove] = None,
                  diagnose: Optional[Callable[..., Any]] = None, logic_fixer: Optional[Callable[..., Dict[str, Any]]] = None,
                  see: Optional[Callable[..., page_tests.Verdict]] = None) -> Dict[str, Any]:
    """Has the app changed so that a red rule's test turns green. Where the fault lies is found first
    (`onboarding/rule_diagnosis.py`), and that decides what is changed: the page (`rule_fix.py`), the record's class
    through the test-first loop (`logic_fix.py`), or nothing, when the rules disagree or the test is wrong. The
    answer says which (`fault`, `why`, `rules`), and a rule left red keeps it as the `cause` beside its light.

    Either change is guarded by the rules that are green: it is kept only when they all still are. A kept change is
    followed by a run of the rule's test, so the light that turns green is one that was seen."""
    from onboarding import logic_fix, rule_diagnosis, rule_fix
    from onboarding.product_contract import stored_contract
    fixer, logic_fixer = fixer or rule_fix.fix_rule, logic_fixer or logic_fix.fix_logic
    diagnose, see = diagnose or rule_diagnosis.diagnose_rule, see or page_tests.run_test
    workspace_dir, page_url = workspace_dir or _workspace(), page_url or _page_url()
    with uow:
        state = uow.kickstart.get()
        card, spec = _find(state, spec_id)
        card, spec = (dict(card) if card else None), (dict(spec) if spec else None)
        green = {c["id"]: c["page_test"]["source"] for c in (state.rule_cards or [])
                 if c.get("id") != spec_id and c.get("is_active", True)
                 and (c.get("page_test") or {}).get("status") == page_tests.PASS and c["page_test"].get("source")}
        contract, manifest = stored_contract(state), dict(state.action_manifest or {})
        titles = {str(r.get("id") or r.get("spec_id")): str(r.get("title") or "")
                  for r in [*(state.inbox_specs or []), *(state.rule_cards or [])]}
    if card is None and spec is None:
        return {"success": False, "status": "not_found", "reason": f"Rule {spec_id} not found."}
    rule = _rule(card, spec, spec_id)
    stored = dict((card or {}).get("page_test") or (spec or {}).get("page_test") or {})

    def answer(result: Dict[str, Any], diagnosis: Any = None) -> Dict[str, Any]:
        cause = {"fault": diagnosis.fault, "why": diagnosis.why, "rules": list(diagnosis.rules)} if diagnosis else {}
        fixed = result["status"] == rule_fix.FIXED
        if fixed:
            run_rule_test(spec_id, uow=uow, workspace_dir=workspace_dir, page_url=page_url, prove=prove)
        elif cause:
            record_page_test(spec_id, {**stored, "cause": cause}, uow=uow, ran_at=stored.get("ran_at"))
        return {"success": fixed, "spec_id": spec_id, **cause, **result}

    if stored.get("status") != page_tests.FAIL:
        return answer(_not_changed(rule_fix.NOT_RED, "a fix starts from a rule whose test ran and failed"))
    if str(rule.get("action") or "").strip() and not stored.get("seen"):
        # the stored run is from before the app's side was noted: the test is run once more to see it
        verdict = see(workspace_dir, spec_id, stored["source"], page_url)
        stored.update(status=verdict.status, reason=verdict.reason, evidence=verdict.evidence, seen=verdict.seen)
        record_page_test(spec_id, stored, uow=uow)
        if verdict.status != page_tests.FAIL:
            return answer(_not_changed(rule_fix.NOT_RED, f"the rule's test no longer fails: it ended as {verdict.status}"))
    try:
        diagnosis = diagnose(rule, stored, contract, workspace_dir)
    except rule_diagnosis.NoDiagnosis as err:  # a provider or parse error: reported with its reason, never retried
        return answer(_not_changed(rule_fix.NOT_FIXED, f"the cause was not found: {err}"))

    if diagnosis.fault == rule_diagnosis.PAGE:
        result = fixer(rule, stored, workspace_dir, page_url, green)
    elif diagnosis.fault == rule_diagnosis.LOGIC:
        result = dict(logic_fixer(rule, stored, workspace_dir, manifest,
                                  check=lambda: rule_fix.check_app(workspace_dir, page_url, rule, stored, green)))
        tdd = result.pop("tdd", None)
        if tdd is not None:
            from service_layer import services
            services.record_tdd_result(spec_id, tdd, uow=uow)
        # the rules whose own tests the change broke: this rule and those could not be kept together
        broke = set(result.pop("broke", None) or [])
        diagnosis.rules = [title for other, title in titles.items() if other != spec_id and title
                           and os.path.basename(logic_fix.unit_test_path({"spec_id": other}, workspace_dir)) in broke]
        if diagnosis.rules:
            result["reason"] = ("a change that makes this rule hold breaks: "
                                + ", ".join(f'"{title}"' for title in diagnosis.rules))
    else:  # the rules disagree, or the test is wrong: no change of code is the right one
        result = _not_changed(rule_fix.NOT_FIXED, diagnosis.why)
    return answer(result, diagnosis)


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
