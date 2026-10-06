"""
Unit tests for Dynamic Architectural Synthesizer & Dynamic Test Generator.
Verifies 100% domain-agnostic, category-free first-principles synthesis.
Zero hardcoded domain keywords permitted.
"""

import ast
import re
import pytest
from onboarding.router_engine import (
    DomainStructureSchema,
    EntitySpec,
    AttributeSpec,
    BusinessSpec
)


def _contains_hardcoded_domain_terms(code: str) -> bool:
    """Verifies that no domain keywords are hardcoded in the engine module."""
    banned_literals = ["chess", "pawn", "knight", "bishop", "rook", "hotel", "pallet", "pizza"]
    code_lower = code.lower()
    for term in banned_literals:
        # Check for string literal matches in code
        if f'"{term}"' in code_lower or f"'{term}'" in code_lower:
            return True
    return False


def test_dynamic_synthesizer_code_has_zero_hardcoded_domain_keywords():
    """Engine purity check: dynamic_architectural_synthesizer.py must contain 0 domain literals."""
    import inspect
    import onboarding.dynamic_architectural_synthesizer as das
    src = inspect.getsource(das)
    assert not _contains_hardcoded_domain_terms(src), "Found hardcoded domain keywords in dynamic synthesizer!"


def test_synthesize_modular_architecture_contract_chess_domain():
    """Tests dynamic contract synthesis for a game/interactive domain without categories."""
    from onboarding.dynamic_architectural_synthesizer import synthesize_dynamic_architecture_contract

    structure = DomainStructureSchema(
        domain_name="ChessGame",
        entities=[
            EntitySpec(
                name="Game",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="board", type="dict"),
                    AttributeSpec(name="turn", type="str"),
                    AttributeSpec(name="history", type="list")
                ]
            ),
            EntitySpec(
                name="Move",
                is_aggregate_root=False,
                attributes=[
                    AttributeSpec(name="from_square", type="str"),
                    AttributeSpec(name="to_square", type="str"),
                    AttributeSpec(name="piece", type="str")
                ]
            )
        ]
    )

    specs = [
        BusinessSpec(
            spec_id="SPEC-01",
            title="Turn Alternation",
            description="Active player alternates after each legal move",
            given_when_then="GIVEN active player is White WHEN a legal move is executed THEN active player becomes Black",
            target_aggregate="Game"
        ),
        BusinessSpec(
            spec_id="SPEC-02",
            title="Invalid Move Rejection",
            description="Illegal moves are rejected",
            given_when_then="GIVEN active player WHEN an illegal move is attempted THEN raise 400 error and keep turn unchanged",
            target_aggregate="Game"
        )
    ]

    contract = synthesize_dynamic_architecture_contract(
        pitch="A chess app",
        structure=structure,
        inbox_specs=specs,
        rel_workspace="workspace"
    )

    assert "Single Source of Truth" in contract
    assert "Component Modularity" in contract
    assert "Turn Alternation" in contract
    assert "Invalid Move Rejection" in contract
    assert "workspace/src/domain/" in contract
    assert "workspace/frontend/src/" in contract


def test_synthesize_modular_architecture_contract_medical_triage_domain():
    """Tests dynamic contract synthesis for a completely different medical domain."""
    from onboarding.dynamic_architectural_synthesizer import synthesize_dynamic_architecture_contract

    structure = DomainStructureSchema(
        domain_name="EmergencyTriage",
        entities=[
            EntitySpec(
                name="TriageQueue",
                is_aggregate_root=True,
                attributes=[
                    AttributeSpec(name="patients", type="list"),
                    AttributeSpec(name="current_capacity", type="int")
                ]
            ),
            EntitySpec(
                name="Patient",
                is_aggregate_root=False,
                attributes=[
                    AttributeSpec(name="triage_level", type="int"),
                    AttributeSpec(name="heart_rate", type="int")
                ]
            )
        ]
    )

    specs = [
        BusinessSpec(
            spec_id="SPEC-01",
            title="Acuity Priority Invariant",
            description="Level 1 patients must be placed at front of queue",
            given_when_then="GIVEN a patient with acuity 1 WHEN enrolled THEN place immediately at front of queue",
            target_aggregate="TriageQueue"
        )
    ]

    contract = synthesize_dynamic_architecture_contract(
        pitch="An emergency hospital triage queue",
        structure=structure,
        inbox_specs=specs,
        rel_workspace="workspace"
    )

    assert "Single Source of Truth" in contract
    assert "Acuity Priority Invariant" in contract
    assert "workspace/src/domain/" in contract


def test_dynamic_test_generator_creates_valid_python_suite():
    """Tests dynamic acceptance test generator producing valid executable pytest AST."""
    from onboarding.dynamic_test_generator import generate_dynamic_acceptance_suite

    specs = [
        BusinessSpec(
            spec_id="SPEC-01",
            title="Turn Alternation",
            description="Active player alternates after each legal move",
            given_when_then="GIVEN active player is White WHEN a legal move is executed THEN active player becomes Black",
            target_aggregate="Game"
        ),
        BusinessSpec(
            spec_id="SPEC-02",
            title="Invalid Move Rejection",
            description="Illegal moves are rejected",
            given_when_then="GIVEN active player WHEN an illegal move is attempted THEN raise 400 error and keep turn unchanged",
            target_aggregate="Game"
        )
    ]

    test_code = generate_dynamic_acceptance_suite("ChessGame", specs)
    assert "def test_turn_alternation" in test_code
    assert "def test_invalid_move_rejection" in test_code
    
    # Must be valid Python syntax
    parsed = ast.parse(test_code)
    assert parsed is not None
