"""
Unit tests for the 4-Node Deterministic Compiler Graph (Nodes 2 & 3).
Verifies:
1. Action protocol synthesis names the user-facing actions without writing code (the aggregate belongs to the skeleton + TDD loop).
2. Presentation projection synthesis writes modular UI & client with App.tsx < 100 LOC.
3. Zero hardcoded domain keywords in synthesizers and prompt templates.
"""

import os
import pytest
from onboarding.router_engine import DomainStructureSchema, EntitySpec, AttributeSpec, BusinessSpec
from onboarding.domain_engine_synthesizer import synthesize_action_protocol
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


def test_synthesize_action_protocol_writes_no_domain_code(tmp_path):
    """Verify the synthesizer returns an action manifest and leaves the aggregate and router alone.

    id: TST-CG-001
    Given: A structure and specs
    When: The action protocol is synthesized
    Then: It succeeds with a manifest, writes no files, and does not create the aggregate, state, rules or router
    """
    ws_dir = str(tmp_path)
    structure = DomainStructureSchema(
        domain_name="InventorySystem",
        entities=[EntitySpec(name="InventoryItem", is_aggregate_root=True, attributes=[
            AttributeSpec(name="sku", type="str", required=True),
            AttributeSpec(name="stock", type="int", required=True)])]
    )
    inbox_specs = [BusinessSpec(
        spec_id="SPEC-001", title="Non-Negative Stock Invariant", description="Stock cannot fall below zero",
        given_when_then="Given an item When decremented beyond zero Then raises InvariantError",
        target_aggregate="InventoryItem")]

    result = synthesize_action_protocol(
        pitch="An automated inventory management system tracking item stocks.",
        structure=structure, inbox_specs=inbox_specs, workspace_dir=ws_dir)

    assert result["success"] is True
    assert result["files"] == []
    assert result["action_manifest"]["actions"]
    assert not os.path.exists(os.path.join(ws_dir, "src"))


def test_action_protocol_prompt_shows_the_real_domain_class(tmp_path, monkeypatch):
    """Verify the prompt is grounded in the skeleton's dataclass instead of a made-up model.

    id: TST-CG-002
    Given: A skeleton domain module on disk
    When: The action protocol is synthesized
    Then: The prompt contains that class's source and the spec text
    """
    import agent_orchestrator
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    (domain / "inventory_item.py").write_text("@dataclass\nclass InventoryItem:\n    sku: str\n    stock: int\n")
    seen = {}

    def fake(prompt, stage="general", **kwargs):
        seen["prompt"] = prompt
        return '{"action_manifest": {"actions": []}}'

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    structure = DomainStructureSchema(domain_name="Inv", entities=[EntitySpec(
        name="InventoryItem", is_aggregate_root=True, attributes=[AttributeSpec(name="sku", type="str", required=True)])])
    spec = BusinessSpec(spec_id="S1", title="T", description="d", given_when_then="Given X When Y Then Z",
                        target_aggregate="InventoryItem")
    synthesize_action_protocol("p", structure, [spec], str(tmp_path))
    assert "stock: int" in seen["prompt"] and "Given X When Y Then Z" in seen["prompt"]


def test_action_protocol_failure_reports_the_reason(tmp_path, monkeypatch):
    """Verify an unusable LLM answer is reported, not replaced by an invented default action.

    id: TST-CG-003
    Given: The LLM returns something that is not an action manifest
    When: The action protocol is synthesized
    Then: success is False, the error says why, and there are no invented actions
    """
    import agent_orchestrator
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda *a, **k: '{"something": "else"}')
    structure = DomainStructureSchema(domain_name="Inv", entities=[])
    result = synthesize_action_protocol("p", structure, [], str(tmp_path))
    assert result["success"] is False and "action_manifest" in result["error"]
    assert result["action_manifest"] == {"actions": []}


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
           "documented in the old handover notes #18 and #19 (git history: vault/HANDOVER-archive.md); they never reached git. "
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
