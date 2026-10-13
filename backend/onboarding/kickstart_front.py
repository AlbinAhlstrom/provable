"""The front of a kickstart: from a pitch to what the builders start from.

A live kickstart writes the product contract (`product_contract.py`, ADR-011): one call, and the domain structure,
the rule deck, the intent, the action manifest and the page's blueprint are read out of it. The earlier front
(intent, then expansion, then decomposition, with the action protocol and the UX plan as stages of their own
afterwards) is still what an offline or mock kickstart runs, and a live one when `KICKSTART_FRONT=stages`, so the two
can be compared on the same pitch.
"""

import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from onboarding.intent import ProductIntent
from onboarding.router_engine import BusinessSpec, DomainStructureSchema
from run_recorder import stage_begin

CONTRACT, STAGES = "contract", "stages"


@dataclass
class Front:
    intent: ProductIntent
    pitch_text: str                       # what later writers read as the product's specification
    structure: DomainStructureSchema
    inbox_specs: List[BusinessSpec]
    stored_pitch: str = ""                # what is kept as the product's specification (a page rebuild plans from it)
    contract: Optional[Any] = None        # the ProductContract, when the front was one
    timings: Dict[str, float] = field(default_factory=dict)

    def stage_overrides(self) -> Dict[str, Any]:
        """The synthesis stages the contract already answers (`run_synthesis_stages` keyword arguments)."""
        if self.contract is None:
            return {}
        from onboarding.product_contract import contract_protocol, contract_review, contract_ux
        return {"protocol": contract_protocol(self.contract), "ux": contract_ux(self.contract),
                "review": contract_review(self.contract)}


def front_kind(live: bool) -> str:
    return CONTRACT if live and (os.environ.get("KICKSTART_FRONT") or CONTRACT).strip().lower() != STAGES else STAGES


def contract_front(pitch: str) -> Front:
    """The front as one stage: the product contract and everything read out of it."""
    from onboarding.product_contract import write_product_contract
    started = time.time()
    st = stage_begin(CONTRACT)
    try:
        contract = write_product_contract(pitch)
    except Exception as exc:
        st.fail(f"{type(exc).__name__}: {exc}")
        raise
    structure, specs = contract.structure(), contract.specs()
    st.note("records", [e.name for e in structure.entities])
    st.note("actions", [a.name for a in contract.actions])
    st.note("rules", {"api": sum(1 for r in contract.rules if r.kind == "api"),
                      "page": sum(1 for r in contract.rules if r.kind == "page")})
    st.ok()
    brief = contract.brief()
    return Front(intent=contract.intent(), pitch_text=brief, structure=structure, inbox_specs=specs, contract=contract,
                 stored_pitch=brief + "\n\n## The page\n" + contract.blueprint(),
                 timings={"0_contract": round(time.time() - started, 2)})


def staged_front(pitch: str, expand: bool) -> Front:
    """The front as three stages in a row: intent, expansion (only when `expand`), decomposition."""
    from onboarding import intent as intent_step
    from onboarding.prompt_expander import expand_pitch_into_interactive_specification
    from onboarding.router_engine import decompose_pitch_into_structure_and_inbox

    timings: Dict[str, float] = {}
    # Decide what kind of product the user asked for from their own words, before any expansion can inflate the scope
    st = stage_begin("intent")
    product_intent = intent_step.classify_pitch_intent(pitch)
    st.ok()

    started = time.time()
    st = stage_begin("expansion")
    pitch_text = pitch
    if expand:
        print("[Kickstart] [0/5] Grounding intent: expanding pitch into interactive full-stack specification...", flush=True)
        pitch_text = expand_pitch_into_interactive_specification(pitch, intent=product_intent)
        timings["0_intent_grounding"] = round(time.time() - started, 2)
        print(f"[Kickstart] [0/5] ✓ Specification expanded ({len(pitch_text.split())} words) in {timings['0_intent_grounding']}s", flush=True)
    else:
        timings["0_intent_grounding"] = 0.0
    st.ok()

    started = time.time()
    print("[Kickstart] [1/5] Decomposing pitch into domain aggregates and inbox specs...", flush=True)
    st = stage_begin("decomposition")
    decomp = decompose_pitch_into_structure_and_inbox(pitch_text, intent=product_intent)
    st.ok()
    inbox_specs = decomp.inbox.specs if hasattr(decomp, "inbox") and hasattr(decomp.inbox, "specs") else []
    timings["1_decomposition"] = round(time.time() - started, 2)
    return Front(intent=product_intent, pitch_text=pitch_text, structure=decomp.structure, inbox_specs=inbox_specs,
                 stored_pitch=pitch_text, timings=timings)


def build_front(pitch: str, live: bool) -> Front:
    """What the builders start from. `live` is False for an offline or mock kickstart, which writes no contract."""
    return contract_front(pitch) if front_kind(live) == CONTRACT else staged_front(pitch, expand=live)
