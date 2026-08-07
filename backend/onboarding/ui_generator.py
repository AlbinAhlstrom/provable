"""
LLM-Driven Dynamic UI Synthesizer powered by Multi-Agent Planning Engine.

Generates beautiful, domain-tailored React 18 frontend interfaces (`App.tsx`)
using multi-agent layout classification, component registry grounding, and AST self-healing verification gates.
"""

import os
import json
import re
from typing import Dict, Any, List
from onboarding.frontend_planning_engine import (
    run_frontend_planning_pipeline, assemble_app_tsx_from_blueprint
)


def generate_llm_ui(pitch: str, schema: Dict[str, Any], selected_blocks: List[str] = None) -> str:
    """
    Synthesizes a full-featured React 18 `App.tsx` component using the Multi-Agent Planning Engine.
    """
    try:
        print(f"[ui_generator] Launching Multi-Agent Planning Pipeline for pitch: '{pitch[:45]}...'")
        blueprint = run_frontend_planning_pipeline(pitch)
        
        print(f"[ui_generator] Layout Category: '{blueprint.category_layout.category_id}' ({blueprint.category_layout.layout_name})")
        print(f"[ui_generator] Reused Registry Blocks: {blueprint.components.reused_registry_blocks}")
        print(f"[ui_generator] Bespoke Components: {[b.component_name for b in blueprint.components.bespoke_components]}")

        tsx_code = assemble_app_tsx_from_blueprint(blueprint)
        return tsx_code

    except Exception as e:
        print(f"[ui_generator] Multi-Agent Planning Pipeline notice: {e}")
        return None
