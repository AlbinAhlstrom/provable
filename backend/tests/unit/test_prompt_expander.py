"""
Unit tests for Autonomous Intent Grounding (Prompt Expander).
Verifies 100% domain-agnostic expansion from terse pitches into explicit specifications.
Strictly zero hardcoded domain keywords.
"""

import inspect
import pytest


def _contains_hardcoded_domain_terms(code: str) -> bool:
    """Verifies that no domain keywords are hardcoded in the engine module."""
    banned_literals = ["chess", "pawn", "knight", "bishop", "rook", "hotel", "pallet", "pizza", "tictactoe"]
    code_lower = code.lower()
    for term in banned_literals:
        if f'"{term}"' in code_lower or f"'{term}'" in code_lower:
            return True
    return False


def test_prompt_expander_code_has_zero_hardcoded_domain_keywords():
    """Engine purity check: prompt_expander.py must contain 0 domain literals."""
    import onboarding.prompt_expander as pe
    src = inspect.getsource(pe)
    assert not _contains_hardcoded_domain_terms(src), "Found hardcoded domain keywords in prompt_expander.py!"


def test_prompt_expansion_template_has_zero_hardcoded_domain_keywords():
    """Template purity check: prompt_expansion.md must contain 0 hardcoded domain branches."""
    import os
    template_path = os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "prompt_expansion.md")
    assert os.path.exists(template_path), "prompt_expansion.md prompt template missing!"
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert not _contains_hardcoded_domain_terms(content), "Found hardcoded domain keywords in prompt_expansion.md!"


def test_expand_pitch_returns_expanded_specification(monkeypatch):
    """Tests that expand_pitch_into_interactive_specification properly calls orchestrator and returns rich spec."""
    from onboarding.prompt_expander import expand_pitch_into_interactive_specification

    mock_expansion = """### 1. Interactive UI Experience
- Render an interactive spatial board with element selection and interaction highlights.
- Visual affordances: coordinate indicators, action status, and move logs.

### 2. Backend DDD Domain Model
- Aggregate Root: ActiveMatch (state representation, rule policy).
- Invariants: Turn alternation and boundary validation.
"""
    import agent_orchestrator
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage: mock_expansion)

    spec = expand_pitch_into_interactive_specification("A terse app pitch")
    assert "Interactive UI Experience" in spec
    assert "Backend DDD Domain Model" in spec
    assert "Aggregate Root" in spec


def test_expand_pitch_fails_loudly_when_the_llm_fails(monkeypatch):
    """Verify an expansion failure is raised with its reason, not hidden behind the unexpanded pitch.

    id: TST-EXP-004
    Given: The LLM call returns nothing, or raises
    When: The pitch is expanded
    Then: ExpansionError carries the reason (policy: no fallbacks on error)
    """
    import pytest
    import agent_orchestrator
    from onboarding.prompt_expander import ExpansionError, expand_pitch_into_interactive_specification

    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **kw: None)
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "quota exceeded", raising=False)
    with pytest.raises(ExpansionError, match="quota exceeded"):
        expand_pitch_into_interactive_specification("A terse app pitch")

    def boom(prompt, stage="general", **kw):
        raise ConnectionError("network down")

    monkeypatch.setattr(agent_orchestrator, "call_gemini", boom)
    with pytest.raises(ExpansionError, match="network down"):
        expand_pitch_into_interactive_specification("A terse app pitch")
