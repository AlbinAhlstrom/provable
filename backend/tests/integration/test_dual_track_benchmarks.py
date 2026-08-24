import pytest
import os
import shutil
from onboarding.router_engine import decompose_pitch_into_structure_and_inbox
from onboarding.skeleton_builder import generate_fullstack_skeleton_files, build_and_write_skeleton
from service_layer.tdd_machine import (
    evaluate_red_gate_result,
    evaluate_green_gate_result,
    TddExecutionState
)

def test_dual_track_benchmark_track_a_pizza_ordering(tmp_path):
    """
    Dual-Track Benchmark — Track A (B2C Transactional Domain):
    Pizzeria Ordering with custom toppings, size multipliers, and minimum order rules.
    """
    pitch = "A pizzeria application where customers order pizzas with custom toppings, size pricing multipliers, and minimum order amount of $15."
    
    # 1. Intake & Routing Decomposition
    result = decompose_pitch_into_structure_and_inbox(pitch)
    assert result.structure.domain_name != ""
    assert len(result.structure.entities) >= 1
    assert len(result.inbox.specs) >= 2
    
    # Verify entity SRP separation
    entity_names = [e.name for e in result.structure.entities]
    assert any("Pizza" in name or "Order" in name for name in entity_names)
    
    # 2. Scaffold Full-Stack Domain & OpenAPI Skeleton
    target_dir = str(tmp_path / "track_a_pizza")
    created_files = build_and_write_skeleton(result.structure, target_dir=target_dir)
    
    assert len(created_files) >= 5
    assert any("domain" in p and "pizza" in p.lower() for p in created_files)
    assert any("schemas.py" in p for p in created_files)
    assert any("app.py" in p for p in created_files)
    
    # 3. Simulate Deterministic TDD Red-Gate Loop for Each Spec
    for spec in result.inbox.specs:
        state = TddExecutionState(spec=spec)
        state.advance_to_red()
        
        # Verify Red-Gate correctly approves failing test and rejects tautology
        red_eval_tautology = evaluate_red_gate_result(exit_code=0)
        assert red_eval_tautology["approved"] is False
        
        red_eval_approved = evaluate_red_gate_result(exit_code=1, report_json={"summary": {"failed": 1}})
        assert red_eval_approved["approved"] is True
        
        # Verify Green-Gate approves passing implementation
        state.advance_to_green()
        green_eval = evaluate_green_gate_result(exit_code=0)
        assert green_eval["approved"] is True
        assert state.is_dead_end() is False


def test_dual_track_benchmark_track_b_industrial_fifo_warehouse(tmp_path):
    """
    Dual-Track Benchmark — Track B (Complex Industrial Domain):
    Automated Warehouse Management enforcing FIFO pallet allocation, temperature zone constraints, and hazard segregation.
    """
    pitch = "An automated warehouse management system enforcing strict FIFO pallet allocation, temperature-controlled zone constraints, and hazard class segregation rules."
    
    # 1. Intake & Routing Decomposition
    result = decompose_pitch_into_structure_and_inbox(pitch)
    assert result.structure.domain_name != ""
    assert len(result.structure.entities) >= 1
    assert len(result.inbox.specs) >= 2
    
    # 2. Verify Boundary Flags
    boundary_specs = [s for s in result.inbox.specs if s.is_mathematical_boundary]
    assert len(boundary_specs) >= 1
    
    # 3. Scaffold Full-Stack Domain & OpenAPI Skeleton
    target_dir = str(tmp_path / "track_b_warehouse")
    created_files = build_and_write_skeleton(result.structure, target_dir=target_dir)
    
    assert len(created_files) >= 5
    assert any("domain" in p for p in created_files)
    assert any("repository.py" in p for p in created_files)
    assert any("app.py" in p for p in created_files)
    
    # 4. Simulate Deterministic TDD Red-Gate Loop for Industrial Rules
    for spec in result.inbox.specs:
        state = TddExecutionState(spec=spec)
        state.advance_to_red()
        
        # Verify RED Gate
        red_eval = evaluate_red_gate_result(exit_code=1)
        assert red_eval["approved"] is True
        
        # Verify GREEN Gate
        state.advance_to_green()
        green_eval = evaluate_green_gate_result(exit_code=0)
        assert green_eval["approved"] is True
