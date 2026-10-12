"""What a rule's page test says about it, as the one status the Studio shows: not run, pass, broken or fail.

A rule is proved by a test that drives the running page, and by nothing else (ADR-010). The test's last run ended in
one of three ways: every assertion held (pass), one did not (fail), or the test could not judge (broken). A rule
whose page test never ran is not run, whatever a test of the domain class said about it. Pure: no I/O.
"""
from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Tuple

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
    """The status and one-line reason of whatever holds a rule's `page_test` (a rule card or a stored spec)."""
    ran = (stored or {}).get("page_test") or {}
    try:
        status = SpecTestStatus(ran.get("status"))
    except ValueError:
        return SpecTestStatus.NOT_RUN, None
    if status in (SpecTestStatus.PASS, SpecTestStatus.NOT_RUN):
        return status, None
    return status, _one_line(ran.get("reason"))


def with_test_status(cards: Iterable[Dict[str, Any]], stored_specs: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Copies of the rule cards, each carrying `test_status` and `test_reason` from its own page test, or from the
    one stored with the spec of its id."""
    by_id = {s.get("spec_id"): s for s in stored_specs}
    out = []
    for card in cards:
        status, reason = derive_test_status(card if card.get("page_test") else by_id.get(card.get("id")))
        out.append({**card, "test_status": status.value, "test_reason": reason})
    return out
