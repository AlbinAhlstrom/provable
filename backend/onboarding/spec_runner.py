"""
Spec runner: the kickstart runs the rule deck's behaviour specs itself.

The actions' methods (`action_behaviour.py`) give a generated app its basic behaviour. The specs are its rules: a move
must be legal, a stylist cannot be double-booked. Left for the user to run one by one, a fresh app enforces none of
them. So each behaviour spec goes through the TDD loop during the kickstart, while the page is being written.

- Together: every spec's test is written side by side, then each class gets one code answer for all of its rules,
  judged test by test (`service_layer/tdd_batch.py`). One after another, the deck was most of a kickstart's duration.
- A spec that does not reach GREEN is named here with its reason; the others stand. Nothing is retried beyond the
  loop's own single retry.
- Presentation specs are not run: the page is written from them in the same kickstart.
- The first test of every behaviour spec can be written ahead (`draft_behaviour_tests`), while the actions are being
  implemented; the loop then starts from those tests.

How the specs are executed, and where a spec's status is stored, belongs to the caller (`execute`).
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from onboarding.router_engine import BusinessSpec, SpecKind
from pipeline_trace import traced


@dataclass
class SpecRun:
    """Which of the deck's behaviour specs the kickstart fulfilled."""
    fulfilled: List[str] = field(default_factory=list)
    unfulfilled: List[Dict[str, str]] = field(default_factory=list)   # {spec_id, title, status, error}
    skipped: str = ""

    @property
    def success(self) -> bool:
        return not self.unfulfilled

    @property
    def error(self) -> str:
        return "; ".join(f"{u['spec_id']} ({u['title']}): {u['error'] or u['status']}" for u in self.unfulfilled)


@dataclass
class RuleProgress:
    """How far the deck's behaviour specs have come: shown to the user while the app is being built."""
    done: int = 0      # specs that went through the loop, whatever the outcome
    total: int = 0
    active: int = 0    # of those, the ones the app now enforces
    latest: str = ""   # title of the rule that became active last
    waiting: List[str] = field(default_factory=list)  # ids of the specs in the loop that are not settled yet


Execute = Callable[[List[BusinessSpec], Callable[[BusinessSpec, Dict[str, Any]], None]], Any]


def _behaviour(specs: List[BusinessSpec]) -> List[BusinessSpec]:
    return [s for s in specs if getattr(s, "kind", SpecKind.BEHAVIOR.value) == SpecKind.BEHAVIOR.value]


def draft_behaviour_tests(specs: List[BusinessSpec], write: Callable[[List[BusinessSpec]], Dict[str, Any]]) -> Dict[str, Any]:
    """Hands every behaviour spec to `write` (the TDD batch's test drafting) and returns what it wrote, by spec id."""
    behaviour = _behaviour(specs)
    return write(behaviour) if behaviour else {}


@traced("specs.run_behaviour_specs")
def run_behaviour_specs(specs: List[BusinessSpec], execute: Execute,
                        report: Optional[Callable[[RuleProgress], None]] = None) -> SpecRun:
    """Hands every behaviour spec to `execute` (the TDD batch), which tells its second argument each spec's result as
    it is settled. `report` is told how far the deck has come before the first spec and after each one."""
    behaviour = _behaviour(specs)
    if not behaviour:
        return SpecRun(skipped="the deck has no behaviour spec")
    results: Dict[str, Dict[str, Any]] = {}
    titles: List[str] = []  # of the fulfilled specs, in the order they were settled

    def tell() -> None:
        if report is not None:
            report(RuleProgress(done=len(results), total=len(behaviour), active=len(titles),
                                latest=titles[-1] if titles else "",
                                waiting=[s.spec_id for s in behaviour if s.spec_id not in results]))

    def settled(spec: BusinessSpec, result: Dict[str, Any]) -> None:
        results[spec.spec_id] = result
        if result.get("success"):
            titles.append(spec.title)
        tell()
        print(f"[Compiler:Specs] {spec.spec_id} {spec.title}: {result.get('status')}", flush=True)

    tell()
    try:
        execute(behaviour, settled)
    except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
        for spec in behaviour:
            if spec.spec_id not in results:
                settled(spec, {"success": False, "status": "ERROR", "error": f"{type(err).__name__}: {err}"})

    run = SpecRun()
    for spec in behaviour:  # deck order, whatever order they were settled in
        result = results.get(spec.spec_id) or {"success": False, "status": "ERROR", "error": "the executor gave no result"}
        if result.get("success"):
            run.fulfilled.append(spec.spec_id)
        else:
            run.unfulfilled.append({"spec_id": spec.spec_id, "title": spec.title,
                                    "status": str(result.get("status") or ""), "error": str(result.get("error") or "")})
    return run
