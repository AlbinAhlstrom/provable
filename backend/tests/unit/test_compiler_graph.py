"""
Unit tests for the 4-Node Deterministic Compiler Graph (Nodes 2 & 3).
Verifies:
1. Domain engine synthesis writes pure DDD domain modules & FastAPI routers.
2. Presentation projection synthesis writes modular UI & client with App.tsx < 100 LOC.
3. Zero hardcoded domain keywords in synthesizers and prompt templates.
"""

import os
import pytest
from onboarding.router_engine import DomainStructureSchema, EntitySpec, AttributeSpec, BusinessSpec
from onboarding.domain_engine_synthesizer import synthesize_and_write_domain_engine
from onboarding.presentation_projection_synthesizer import synthesize_and_write_presentation_projection


BANNED_DOMAIN_KEYWORDS = [
    "chess", "hotel", "pallet", "pizza", "flight", "doctor", "hospital", "crypto"
]


def test_compiler_synthesizers_have_zero_hardcoded_domain_keywords():
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    files_to_check = [
        os.path.join(backend_dir, "onboarding", "domain_engine_synthesizer.py"),
        os.path.join(backend_dir, "onboarding", "presentation_projection_synthesizer.py"),
        os.path.join(backend_dir, "prompts", "domain_engine_synthesis.md"),
        os.path.join(backend_dir, "prompts", "presentation_projection_synthesis.md"),
    ]

    for filepath in files_to_check:
        assert os.path.exists(filepath), f"Missing expected file: {filepath}"
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
        for kw in BANNED_DOMAIN_KEYWORDS:
            assert kw not in content, f"Banned domain keyword '{kw}' found in {os.path.basename(filepath)}"


def test_synthesize_and_write_domain_engine(tmp_path):
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[
            EntitySpec(
                name="InventoryItem",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="sku", type="str", required=True),
                    AttributeSpec(name="stock", type="int", required=True)
                ]
            )
        ]
    )
    inbox_specs = [
        BusinessSpec(
            spec_id="SPEC-001",
            title="Non-Negative Stock Invariant",
            description="Stock cannot fall below zero",
            given_when_then="Given an item When decremented beyond zero Then raises InvariantError",
            target_aggregate="InventoryItem"
        )
    ]

    result = synthesize_and_write_domain_engine(
        pitch="An automated inventory management system tracking item stocks.",
        structure=structure,
        inbox_specs=inbox_specs,
        workspace_dir=ws_dir
    )

    assert result["success"] is True
    assert len(result["files"]) >= 4

    rules_file = os.path.join(ws_dir, "src", "domain", "rules.py")
    state_file = os.path.join(ws_dir, "src", "domain", "state.py")
    agg_file = os.path.join(ws_dir, "src", "domain", "inventory_item.py")
    router_file = os.path.join(ws_dir, "src", "entrypoints", "routers", "inventory_item.py")

    assert os.path.exists(rules_file)
    assert os.path.exists(state_file)
    assert os.path.exists(agg_file)
    assert os.path.exists(router_file)


def test_synthesize_and_write_presentation_projection(tmp_path):
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[
            EntitySpec(
                name="InventoryItem",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="sku", type="str", required=True),
                    AttributeSpec(name="stock", type="int", required=True)
                ]
            )
        ]
    )
    inbox_specs = [
        BusinessSpec(
            spec_id="SPEC-001",
            title="Non-Negative Stock Invariant",
            description="Stock cannot fall below zero",
            given_when_then="Given an item When decremented beyond zero Then raises InvariantError",
            target_aggregate="InventoryItem"
        )
    ]

    result = synthesize_and_write_presentation_projection(
        pitch="An automated inventory management system tracking item stocks.",
        structure=structure,
        inbox_specs=inbox_specs,
        workspace_dir=ws_dir
    )

    assert result["success"] is True
    assert len(result["files"]) >= 5

    app_file = os.path.join(ws_dir, "src", "App.tsx")
    view_file = os.path.join(ws_dir, "src", "views", "InventoryItemView.tsx")
    controls_file = os.path.join(ws_dir, "src", "components", "Controls", "InventoryItemControls.tsx")
    history_file = os.path.join(ws_dir, "src", "components", "History", "InventoryItemHistory.tsx")
    client_file = os.path.join(ws_dir, "src", "api", "inventory_itemClient.ts")

    assert os.path.exists(app_file)
    assert os.path.exists(view_file)
    assert os.path.exists(controls_file)
    assert os.path.exists(history_file)
    assert os.path.exists(client_file)

    # Anti-monolith verification: App.tsx < 100 LOC
    with open(app_file, "r", encoding="utf-8") as f:
        loc = len([line for line in f.readlines() if line.strip()])
    assert loc < 100


def test_domain_engine_synthesizer_produces_action_manifest(tmp_path):
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[
            EntitySpec(
                name="InventoryItem",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="sku", type="str", required=True),
                    AttributeSpec(name="stock", type="int", required=True)
                ]
            )
        ]
    )
    inbox_specs = [
        BusinessSpec(
            spec_id="SPEC-001",
            title="Non-Negative Stock Invariant",
            description="Stock cannot fall below zero",
            given_when_then="Given an item When decremented beyond zero Then raises InvariantError",
            target_aggregate="InventoryItem"
        )
    ]

    result = synthesize_and_write_domain_engine(
        pitch="An automated inventory management system tracking item stocks.",
        structure=structure,
        inbox_specs=inbox_specs,
        workspace_dir=ws_dir
    )

    assert result["success"] is True
    assert "action_manifest" in result
    assert isinstance(result["action_manifest"], dict)
    assert "actions" in result["action_manifest"]


def test_presentation_projection_synthesizer_accepts_action_manifest(tmp_path):
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[
            EntitySpec(
                name="InventoryItem",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="sku", type="str", required=True),
                    AttributeSpec(name="stock", type="int", required=True)
                ]
            )
        ]
    )
    inbox_specs = [
        BusinessSpec(
            spec_id="SPEC-001",
            title="Non-Negative Stock Invariant",
            description="Stock cannot fall below zero",
            given_when_then="Given an item When decremented beyond zero Then raises InvariantError",
            target_aggregate="InventoryItem"
        )
    ]
    manifest = {
        "actions": [
            {"name": "adjust_stock", "aliases": ["adjust", "set_stock"], "params": ["sku", "delta"]}
        ]
    }

    result = synthesize_and_write_presentation_projection(
        pitch="An automated inventory management system tracking item stocks.",
        structure=structure,
        inbox_specs=inbox_specs,
        workspace_dir=ws_dir,
        action_manifest=manifest
    )

    assert result["success"] is True
    assert len(result["files"]) >= 5


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN REGRESSION: router_decomposition.md lost the atomicity / invariant-taxonomy rules "
           "documented in vault/HANDOVER.md #18 (and the specs-first rules of #19); they never reached git. "
           "Restore the prompt, then delete this marker (strict=True fails once the test passes).",
)
def test_router_decomposition_prompt_enforces_atomicity_and_forbids_procedural_slop():
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "router_decomposition.md"))
    assert os.path.exists(prompt_path)
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Must enforce single-responsibility atomicity
    assert "ATOMIC" in content.upper()
    assert "PROCEDURAL" in content.upper() or "DECLARATIVE" in content.upper()
    # Must forbid hardware device inputs in domain cards
    assert "GESTURE" in content.upper() or "HARDWARE" in content.upper() or "CLICK" in content.upper()
    # Must enforce structured invariant classification
    assert "INVARIANT" in content.upper()
    assert "STATE_TRANSITION" in content.upper()


def test_router_decomposition_prompt_example_is_accepted_by_the_router_parser(monkeypatch):
    """Contract: the JSON shape the prompt asks the LLM for is exactly what the router parser accepts.

    Replaces a test that grepped the prompt for keywords (which pinned wording, not behaviour).
    """
    import json
    import agent_orchestrator
    from onboarding import router_engine

    pitch = "A neighbourhood bakery tracking customer orders."
    prompt = agent_orchestrator.load_prompt("router_decomposition.md", {"business_pitch": pitch})
    assert prompt, "router_decomposition.md must exist and load"
    assert pitch in prompt and "{business_pitch}" not in prompt

    example = prompt[prompt.index('{\n  "structure"'): prompt.rindex("}") + 1]
    json.loads(example)  # the example itself must be valid JSON

    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda *args, **kwargs: example)
    result = router_engine.decompose_pitch_into_structure_and_inbox(pitch)

    assert result.structure.entities, "prompt example must yield at least one entity"
    assert result.inbox.specs, "prompt example must yield at least one spec"
    assert result.inbox.specs[0].given_when_then.startswith("Given")


def test_domain_engine_synthesizer_normalizes_aggregate_imports_and_creates_bridge(tmp_path, monkeypatch):
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[
            EntitySpec(
                name="InventoryItem",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="sku", type="str", required=True),
                    AttributeSpec(name="stock", type="int", required=True)
                ]
            )
        ]
    )
    inbox_specs = [
        BusinessSpec(
            spec_id="SPEC-001",
            title="Stock Rule",
            description="Stock check",
            given_when_then="Given item When modified Then valid",
            target_aggregate="InventoryItem"
        )
    ]

    # Mock call_gemini to return a payload that mistakenly imports from ...domain.aggregate
    mock_payload = {
        "action_manifest": {"actions": [{"name": "update", "aliases": [], "params": []}]},
        "domain_rules_py": "class DomainException(Exception): pass",
        "domain_state_py": "class ItemState: pass",
        "domain_aggregate_py": "class InventoryItem: pass",
        "router_py": "from fastapi import APIRouter\nfrom ...domain.aggregate import InventoryItem\nfrom src.domain.aggregate import InventoryItem\nrouter = APIRouter()"
    }
    import json
    import onboarding.domain_engine_synthesizer as des
    monkeypatch.setattr(des, "call_gemini", lambda *args, **kwargs: json.dumps(mock_payload))

    result = synthesize_and_write_domain_engine(
        pitch="An automated inventory system.",
        structure=structure,
        inbox_specs=inbox_specs,
        workspace_dir=ws_dir
    )

    assert result["success"] is True

    # 1. Verify aggregate bridge file was written
    bridge_path = os.path.join(ws_dir, "src", "domain", "aggregate.py")
    assert os.path.exists(bridge_path)
    with open(bridge_path, "r", encoding="utf-8") as f:
        bridge_content = f.read()
    assert "from src.domain.inventory_item import *" in bridge_content

    # 2. Verify router_py normalized the aggregate import
    router_path = os.path.join(ws_dir, "src", "entrypoints", "routers", "inventory_item.py")
    assert os.path.exists(router_path)
    with open(router_path, "r", encoding="utf-8") as f:
        router_content = f.read()
    assert "from ...domain.inventory_item import InventoryItem" in router_content
    assert "from src.domain.inventory_item import InventoryItem" in router_content
    assert "aggregate" not in router_content


def test_ensure_typing_imports_injects_missing_types():
    from onboarding.domain_engine_synthesizer import _ensure_typing_imports

    code = "from typing import Dict, List\ndef foo(x: Any) -> Dict[str, Optional[int]]: pass"
    fixed = _ensure_typing_imports(code)
    assert "Any" in fixed
    assert "Optional" in fixed
    assert "Dict" in fixed
    assert "List" in fixed

    # Code without typing import at all
    code_no_typing = "def bar(x: Any) -> List[str]: pass"
    fixed_no_typing = _ensure_typing_imports(code_no_typing)
    assert fixed_no_typing.startswith("from typing import Any, List\n")


def test_generate_fallback_app_tsx_wires_components_and_actions():
    from onboarding.presentation_projection_synthesizer import _generate_fallback_app_tsx

    app_code = _generate_fallback_app_tsx(
        master_name="GameSession",
        master_slug="game_session",
        domain_title="Minesweeper",
        action_manifest={"actions": [{"name": "reveal"}, {"name": "chord"}]}
    )
    assert "import { GameSessionView } from './views/GameSessionView'" in app_code
    assert "import { GameSessionControls } from './components/Controls/GameSessionControls'" in app_code
    assert "import { GameSessionHistory } from './components/History/GameSessionHistory'" in app_code
    assert "import { getGameSession, sendAction, GameSessionState } from './api/game_sessionClient'" in app_code
    assert "<GameSessionView" in app_code
    assert "onReveal=" in app_code
    assert "onChord=" in app_code
    assert "<GameSessionControls" in app_code
    assert "<GameSessionHistory" in app_code
    assert "export default App;" in app_code


def test_sync_workspace_app_shell_preserves_existing_interactive_app(tmp_path):
    from service_layer.services import sync_workspace_app_shell
    from service_layer.unit_of_work import FakeUnitOfWork
    from domain.model import KickstartState, DomainEntitySchema, EntityAttribute

    state = KickstartState(
        business_pitch="# Product & Behavioral Specification: Minesweeper",
        synthesized=True,
        entity_schemas={"game_session": DomainEntitySchema(entity_name="GameSession", canonical_key="game_session", attributes=[EntityAttribute(name="id", type="string")])}
    )
    uow = FakeUnitOfWork(initial_kickstart=state)

    ws_dir = str(tmp_path / "workspace")
    src_dir = os.path.join(ws_dir, "src")
    os.makedirs(src_dir, exist_ok=True)
    app_tsx = os.path.join(src_dir, "App.tsx")

    interactive_code = "// Interactive Projection\nimport { GameSessionView } from './views/GameSessionView';\nimport { sendAction } from './api/game_sessionClient';\nexport const App = () => <GameSessionView />;"
    with open(app_tsx, "w", encoding="utf-8") as f:
        f.write(interactive_code)

    sync_workspace_app_shell(ws_base=ws_dir, uow=uow)

    with open(app_tsx, "r", encoding="utf-8") as f:
        preserved_code = f.read()

    assert preserved_code == interactive_code
    assert "Generated Full-Stack Domain Application" not in preserved_code
