"""
QA opening check: a page that opens showing none of the parts its plan names is a defect.

A page can be tidy on every device and still be nothing: it waits for a record nobody makes, and a person sees a
title and a loading text. Layout, contrast and forms all pass such a page. The plan names the page's parts
(`page_parts.py`), so the opened document is looked through for them, by the same role and name the written files
are checked by.

- None of the parts in the opened document is one defect, with the first parts of the plan named, so the one
  rework knows what a person should have met.
- One part is enough to pass. Which parts are there from the start and which come after a step is the plan's to
  say and the page tests' to prove; this check is the last resort for a page that never gets going, and what makes
  a page get going is decided earlier (who makes the first record is the contract's, `product_contract.OPENED`).
"""

from dataclasses import dataclass, field
from typing import List

from onboarding.page_parts import Part, present_parts
from pipeline_trace import traced

EMPTY = "[Empty opening] "
PARTS_NAMED = 4

_DOCUMENT_SCRIPT = "var root = document.getElementById('root'); return root ? root.outerHTML : '';"


@dataclass
class OpeningCheck:
    """What looking for the plan's parts in the opened page showed. Defects fail the audit."""
    defects: List[str] = field(default_factory=list)
    on_screen: int = 0


@traced("qa.opening_check")
def check_opening(driver, device: str, parts: List[Part]) -> OpeningCheck:
    """Looks through the page as it stands in `driver`, opened and untouched, for the plan's parts."""
    found = present_parts(parts, [driver.execute_script(_DOCUMENT_SCRIPT) or ""])
    if found or not parts:
        return OpeningCheck(on_screen=len(found))
    named = ", ".join(f'"{part.what}"' for part in parts[:PARTS_NAMED])
    return OpeningCheck(defects=[
        f"[{device}] {EMPTY}The page opens showing none of the {len(parts)} parts its plan names ({named}"
        f"{', ...' if len(parts) > PARTS_NAMED else ''}). A person who arrives meets what the plan's Opening section "
        f"describes, without doing anything first."])
