"""
Autonomous Intent Grounding & Pitch Expander.
Transforms concise user pitches into explicit, comprehensive Full-Stack Specifications
by uncovering the intuitive human interaction, primary canvas, and domain invariants.
Strictly domain-agnostic: zero hardcoded domain keywords or rules.
"""

from typing import Optional
import agent_orchestrator
from onboarding.intent import ProductIntent, intent_block


class ExpansionError(RuntimeError):
    """The pitch could not be expanded (provider error or unusable answer). Never papered over with the raw pitch."""


def expand_pitch_into_interactive_specification(pitch: str, intent: Optional[ProductIntent] = None) -> str:
    """
    Expands a concise pitch into an explicit Full-Stack Engineering Specification.
    Uncovers implicit interactive canvas requirements, domain rules, and controls.
    The classified product intent bounds the expansion: it elaborates within that scope and never adds what the
    intent rules out. Returns the rich specification; raises ExpansionError if it cannot be produced.
    """
    clean_pitch = (pitch or "").strip()
    if not clean_pitch:
        return clean_pitch

    # If the user already provided an exhaustive, long-form specification (>250 words), return it directly
    if len(clean_pitch.split()) > 250:
        return clean_pitch

    prompt = agent_orchestrator.load_prompt(
        "prompt_expansion.md",
        {"business_pitch": clean_pitch, "intent_block": intent_block(intent)}
    )
    try:
        response = agent_orchestrator.call_gemini(prompt, stage="prompt_expansion")
    except Exception as e:
        raise ExpansionError(f"Pitch expansion failed: {type(e).__name__}: {e}") from e
    if not (response and isinstance(response, str) and len(response.strip()) > 50):
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty or too-short specification"
        raise ExpansionError(f"Pitch expansion failed: {reason}")
    return response.strip()
