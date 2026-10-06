"""
Autonomous Intent Grounding & Pitch Expander.
Transforms concise user pitches into explicit, comprehensive Full-Stack Specifications
by uncovering the intuitive human interaction, primary canvas, and domain invariants.
Strictly domain-agnostic: zero hardcoded domain keywords or rules.
"""

from typing import Optional
import agent_orchestrator
from onboarding.intent import ProductIntent, intent_block


def expand_pitch_into_interactive_specification(pitch: str, intent: Optional[ProductIntent] = None) -> str:
    """
    Expands a concise pitch into an explicit Full-Stack Engineering Specification.
    Uncovers implicit interactive canvas requirements, domain rules, and controls.
    The classified product intent bounds the expansion: it elaborates within that scope and never adds what the
    intent rules out. Returns the rich specification, or gracefully falls back to the original pitch on error.
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
    if not prompt:
        return clean_pitch

    try:
        response = agent_orchestrator.call_gemini(prompt, stage="prompt_expansion")
        if response and isinstance(response, str) and len(response.strip()) > 50:
            return response.strip()
    except Exception as e:
        print(f"[PromptExpander] Expansion notice: {e}. Preserving original pitch.")

    return clean_pitch
