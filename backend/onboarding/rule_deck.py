"""
The rule deck a kickstart starts with: one card for each rule of the product, and nothing else.

A card is what a person reads in the Studio, so it says the rule in the person's words: a spec from the product
contract carries a plain wording beside the exact line its tests are written from (`BusinessSpec.plain`, ADR-011),
and the card's Given, When and Then are read from the plain one. The exact line stays with the stored spec, which
is where the test writers take it from (`page_tests.rule_text`).

The deck used to be padded with six cards every product got ("Interactive Visual Workspace", "Telemetry & Status
HUD", "Mobile Viewport Containment" and the like). No rule of the product stood behind them and they had no
scenario a test could be written from, so each test writer made one up and its verdict said nothing about the
product. What they stood for is checked for every page by QA (layout on three devices, `qa_auditor.py`).
"""

import re
from typing import Any, Dict, List

from onboarding.router_engine import SpecKind

_CLAUSES = (("given_clause", r"Given\s+(.*?)(?=\s+When\b|\s+Then\b|\s+Unless\b|$)"),
            ("when_clause", r"When\s+(.*?)(?=\s+Then\b|\s+Unless\b|$)"),
            ("then_clause", r"Then\s+(.*?)(?=\s+Unless\b|$)"),
            ("unless_clause", r"Unless\s+(.*?)$"))


def clauses_of(text: str) -> Dict[str, str]:
    """The Given, When, Then and Unless of a rule written as one line, each without the comma that led to the
    next; a clause the line lacks is empty."""
    found = {key: re.search(pattern, text or "", re.IGNORECASE | re.DOTALL) for key, pattern in _CLAUSES}
    return {key: match.group(1).strip().rstrip(",;").rstrip() if match else "" for key, match in found.items()}


def _card(number: int, spec: Dict[str, Any], master_name: str) -> Dict[str, Any]:
    line = spec.get("given_when_then", "")
    clauses = clauses_of(spec.get("plain") or line)
    page_only = spec.get("kind") == SpecKind.PRESENTATION.value
    return {
        "id": spec.get("spec_id") or f"SPEC-{number:03d}",
        "title": spec.get("title") or f"Rule {number}",
        "chapter": spec.get("chapter") or "General",
        "card_type": "VIEW" if page_only else "LOGIC",
        "category": spec.get("category") or ("CALCULATION" if spec.get("is_mathematical_boundary") else "INVARIANT"),
        "target": spec.get("target_aggregate") or master_name,
        "description": spec.get("description", ""),
        "given_clause": clauses["given_clause"] or line,
        "when_clause": clauses["when_clause"],
        "then_clause": clauses["then_clause"],
        "unless_clause": clauses["unless_clause"],
        "is_active": True,
        "status": "ACTIVE",
        "priority": spec.get("priority", "High"),
    }


def deck_cards(specs: List[Any], master_name: str) -> List[Dict[str, Any]]:
    """One card for each spec, in the specs' order."""
    return [_card(number, spec.model_dump() if hasattr(spec, "model_dump") else dict(spec), master_name)
            for number, spec in enumerate(specs, start=1)]
