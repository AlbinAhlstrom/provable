"""
Spec runner: the kickstart runs the rule deck's behaviour specs itself.

The actions' methods (`action_behaviour.py`) give a generated app its basic behaviour. The specs are its rules: a move
must be legal, a stylist cannot be double-booked. Left for the user to run one by one, a fresh app enforces none of
them. So each behaviour spec goes through the TDD loop during the kickstart, while the page is being written.

- One after another, in deck order: every spec's test is written knowing the tests before it, and the loop's
  regression gate re-runs all of them.
- A spec that does not reach GREEN is rolled back by the loop and named here with its reason; the specs after it
  still run. Nothing is retried beyond the loop's own single retry.
- Presentation specs are not run: the page is written from them in the same kickstart.

How a spec is executed, and where its status is stored, belongs to the caller (`execute`).
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


@traced("specs.run_behaviour_specs")
def run_behaviour_specs(specs: List[BusinessSpec], execute: Callable[[BusinessSpec], Dict[str, Any]],
                        report: Optional[Callable[[RuleProgress], None]] = None) -> SpecRun:
    """Runs every behaviour spec through `execute` (the TDD loop), in order. `report` is told how far the deck has
    come before the first spec and after each one."""
    behaviour = [s for s in specs if getattr(s, "kind", SpecKind.BEHAVIOR.value) == SpecKind.BEHAVIOR.value]
    if not behaviour:
        return SpecRun(skipped="the deck has no behaviour spec")
    run = SpecRun()

    def tell() -> None:
        if report is not None:
            report(RuleProgress(done=len(run.fulfilled) + len(run.unfulfilled), total=len(behaviour), active=len(run.fulfilled)))

    tell()
    for spec in behaviour:
        try:
            result = execute(spec)
        except Exception as err:  # a provider or infrastructure error: reported with its reason, never retried
            result = {"success": False, "status": "ERROR", "error": f"{type(err).__name__}: {err}"}
        if result.get("success"):
            run.fulfilled.append(spec.spec_id)
        else:
            run.unfulfilled.append({"spec_id": spec.spec_id, "title": spec.title,
                                    "status": str(result.get("status") or ""), "error": str(result.get("error") or "")})
        tell()
        print(f"[Compiler:Specs] {spec.spec_id} {spec.title}: {result.get('status')}", flush=True)
    return run
