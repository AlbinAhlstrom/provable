"""What a spec's last run says about it, as the one status the Studio shows: not run, pass, broken or fail.

A run ends in one of three ways. The change was proved (pass). A verifying step judged the change and rejected it
after its one retry (fail). Or the run stopped before the behaviour could be judged at all: the test was rejected,
the domain did not import, the provider failed, there was no view to change (broken). Pure: no I/O.
"""
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple

PASSED = "FULFILLED"
ENDED_WITHOUT_PASSING = ("REQUIRES_HUMAN_INTERVENTION", "ERROR")
REJECTED_PHASE = "DEAD_END"  # the verifying step ran and said no (tdd_machine, tdd_batch, presentation_specs)


class SpecTestStatus(str, Enum):
    NOT_RUN = "not_run"
    PASS = "pass"
    BROKEN = "broken"
    FAIL = "fail"


def _one_line(reason: Optional[str]) -> Optional[str]:
    for line in (reason or "").splitlines():
        if line.strip():
            return line.strip()
    return None


def derive_test_status(stored: Optional[Dict[str, Any]]) -> Tuple[SpecTestStatus, Optional[str]]:
    """The status and one-line reason of a stored spec (an entry of `KickstartState.inbox_specs`), or of none."""
    status = (stored or {}).get("status")
    if status == PASSED:
        return SpecTestStatus.PASS, None
    if status not in ENDED_WITHOUT_PASSING:
        return SpecTestStatus.NOT_RUN, None
    run = (stored or {}).get("tdd") or {}
    outcome = SpecTestStatus.FAIL if run.get("phase") == REJECTED_PHASE else SpecTestStatus.BROKEN
    return outcome, _one_line(run.get("error"))


def with_test_status(cards: Iterable[Dict[str, Any]], stored_specs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Copies of the rule cards, each carrying `test_status` and `test_reason` from the stored spec with its id."""
    by_id = {s.get("spec_id"): s for s in stored_specs}
    out = []
    for card in cards:
        status, reason = derive_test_status(by_id.get(card.get("id")))
        out.append({**card, "test_status": status.value, "test_reason": reason})
    return out
