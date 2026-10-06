"""The pitch expander must elaborate within the classified product scope, never past it."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.intent import ProductIntent
from onboarding.prompt_expander import expand_pitch_into_interactive_specification

INTENT = ProductIntent(
    product_type="public_website",
    audience="visitors",
    primary_goal="Present the business and let visitors get in touch",
    scope_summary="An informational site with an enquiry form",
    model_focus=["services", "enquiries"],
    out_of_scope=["online booking", "payments"],
)


def _capture(monkeypatch):
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen["prompt"] = prompt
        return "# Expanded specification\n" + "A scoped specification sentence. " * 5

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    return seen


def test_expansion_prompt_carries_the_intent_scope(monkeypatch):
    """Verify the expansion prompt states what the product is and what must not be added.

    id: TST-EXPINT-001
    Given: A pitch classified as a public website that excludes booking and payments
    When: The pitch is expanded with that intent
    Then: The prompt lists the product type, the coverage and the exclusions
    """
    seen = _capture(monkeypatch)
    expand_pitch_into_interactive_specification("A site for a small firm", intent=INTENT)
    assert "public_website" in seen["prompt"]
    assert "online booking" in seen["prompt"] and "payments" in seen["prompt"]
    assert "services" in seen["prompt"]


def test_expansion_without_intent_says_so(monkeypatch):
    """Verify callers without an intent get an explicit marker instead of a silent default.

    id: TST-EXPINT-002
    Given: No intent
    When: The pitch is expanded
    Then: The prompt says the intent is not specified
    """
    seen = _capture(monkeypatch)
    expand_pitch_into_interactive_specification("A site for a small firm")
    assert "not specified" in seen["prompt"]


def test_expansion_template_has_no_domain_specific_examples():
    """Verify the template's examples do not steer every pitch toward one business domain.

    id: TST-EXPINT-003
    Given: The prompt_expansion.md template
    When: It is read
    Then: It contains no childcare/booking examples that bias unrelated pitches
    """
    path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "prompt_expansion.md")
    text = open(path, encoding="utf-8").read().lower()
    for term in ("family services", "care tracker", "booking request", "client booking"):
        assert term not in text
