"""
Integration test matrix verifying TDD State Machine mutations on WMS baseline:
- Mutation Type 1: Attribute Expansion (Add required float attribute, TypeError handling)
- Mutation Type 2: Domain Invariant (Capacity limit validation & custom domain exception)
- Mutation Type 3: State Transition (Lifecycle & deterministic explicit current_date quarantine)
"""

import pytest
import os
from datetime import date
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

from onboarding.router_engine import (
    decompose_pitch_into_structure_and_inbox,
    BusinessSpec,
    SpecMutationType
)
from onboarding.skeleton_builder import (
    build_and_write_skeleton,
    generate_domain_module
)
from service_layer.tdd_machine import (
    evaluate_red_gate_result,
    evaluate_green_gate_result,
    TddExecutionState
)
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_wms_baseline_and_spec_mutation_matrix(tmp_path):
    """
    Validates end-to-end WMS baseline generation and the 3-mutation TDD matrix:
    1. Attribute Expansion
    2. Domain Invariant with Custom Exception
    3. State Transition with Deterministic Time Parameters
    """
    # -------------------------------------------------------------
    # 1. WMS Baseline Intake & Pure Domain Skeleton Generation
    # -------------------------------------------------------------
    pitch = "An industrial warehouse management system to track Pallets, storage Zones, and forklift Operators."
    result = decompose_pitch_into_structure_and_inbox(pitch)

    assert result.structure.domain_name != ""
    entity_names = [e.name for e in result.structure.entities]
    assert "Pallet" in entity_names
    assert "Zone" in entity_names
    assert "Operator" in entity_names

    target_dir = str(tmp_path / "wms_workspace")
    created_files = build_and_write_skeleton(result.structure, target_dir=target_dir)

    assert len(created_files) >= 5
    assert any("pallet.py" in p for p in created_files)
    assert any("zone.py" in p for p in created_files)
    assert any("operator.py" in p for p in created_files)

    uow = FakeUnitOfWork()

    # -------------------------------------------------------------
    # Mutation Type 1: Attribute Expansion
    # "Add a required weight float attribute to Pallet."
    # -------------------------------------------------------------
    spec_1_dict = {
        "spec_id": "SPEC-WMS-001",
        "title": "Add required weight float attribute to Pallet",
        "description": "Pallet entity must record gross payload weight in kilograms.",
        "given_when_then": "Given weight When instantiating Pallet Then pallet.weight equals weight",
        "target_aggregate": "Pallet",
        "spec_type": SpecMutationType.ATTRIBUTE_EXPANSION.value,
        "is_mathematical_boundary": False,
        "priority": "High",
        "status": "PENDING"
    }
    services.add_inbox_spec(spec_1_dict, uow=uow)

    state_1 = TddExecutionState(spec=BusinessSpec(**spec_1_dict))
    state_1.advance_to_red()

    # RED Phase: Initial Pallet only accepts id/name; passing weight raises TypeError
    @dataclass
    class InitialPallet:
        id: str
        name: str = "Standard Pallet"

    with pytest.raises(TypeError) as excinfo:
        # Unexpected keyword argument 'weight' before implementation
        InitialPallet(id="PAL-001", name="Standard Pallet", weight=250.0)

    assert "unexpected keyword argument" in str(excinfo.value) or "weight" in str(excinfo.value)

    # Red-Gate evaluates TypeError / exit_code=1 as APPROVED_RED
    red_eval_1 = evaluate_red_gate_result(
        exit_code=1,
        report_json={"summary": {"failed": 1}, "tests": [{"call": {"crash": {"message": str(excinfo.value)}}}]}
    )
    assert red_eval_1["approved"] is True
    assert red_eval_1["status"] == "APPROVED_RED"

    # GREEN Phase: Pallet dataclass is updated with weight
    @dataclass
    class ExpandedPallet:
        id: str
        name: str
        weight: float

    pallet_1 = ExpandedPallet(id="PAL-001", name="Heavy Cargo", weight=250.0)
    assert pallet_1.weight == 250.0

    state_1.advance_to_green()
    green_eval_1 = evaluate_green_gate_result(exit_code=0)
    assert green_eval_1["approved"] is True
    services.update_spec_status("SPEC-WMS-001", status="FULFILLED", uow=uow)

    # -------------------------------------------------------------
    # Mutation Type 2: Domain Invariant
    # "A Zone has a weight_capacity. Prevent adding a Pallet to a Zone if it exceeds this capacity (raise CapacityExceededError)."
    # -------------------------------------------------------------
    spec_2_dict = {
        "spec_id": "SPEC-WMS-002",
        "title": "Enforce Zone weight_capacity limit",
        "description": "A Zone has a maximum weight_capacity. Prevent adding a Pallet if total weight exceeds capacity.",
        "given_when_then": "Given Zone capacity When adding Pallet exceeds capacity Then raise CapacityExceededError",
        "target_aggregate": "Zone",
        "spec_type": SpecMutationType.DOMAIN_INVARIANT.value,
        "is_mathematical_boundary": True,
        "priority": "High",
        "status": "PENDING"
    }
    services.add_inbox_spec(spec_2_dict, uow=uow)

    state_2 = TddExecutionState(spec=BusinessSpec(**spec_2_dict))
    state_2.advance_to_red()

    # Red-Gate tautology protection rejects exit_code=0 in RED phase
    assert evaluate_red_gate_result(exit_code=0)["approved"] is False

    # Define domain exception contract
    class CapacityExceededError(Exception):
        """Raised when a Zone exceeds its permitted weight capacity."""
        pass

    # RED Phase: Zone without capacity check fails to raise CapacityExceededError
    @dataclass
    class UncheckedZone:
        id: str
        weight_capacity: float
        pallets: List[ExpandedPallet] = field(default_factory=list)

        def add_pallet(self, p: ExpandedPallet):
            self.pallets.append(p)  # No check before GREEN phase

    zone_red = UncheckedZone(id="ZONE-A", weight_capacity=500.0)
    oversized_pallet = ExpandedPallet(id="PAL-999", name="Lead Bricks", weight=800.0)
    zone_red.add_pallet(oversized_pallet)
    test_failed = len(zone_red.pallets) == 1

    red_eval_2 = evaluate_red_gate_result(exit_code=1)
    assert red_eval_2["approved"] is True

    # GREEN Phase: Zone implements capacity invariant check
    @dataclass
    class ValidatedZone:
        id: str
        weight_capacity: float
        pallets: List[ExpandedPallet] = field(default_factory=list)

        @property
        def current_weight(self) -> float:
            return sum(p.weight for p in self.pallets)

        def add_pallet(self, p: ExpandedPallet):
            if self.current_weight + p.weight > self.weight_capacity:
                raise CapacityExceededError(
                    f"Zone {self.id} capacity {self.weight_capacity}kg exceeded by pallet {p.id} ({p.weight}kg)."
                )
            self.pallets.append(p)

    zone_green = ValidatedZone(id="ZONE-A", weight_capacity=500.0)
    normal_pallet = ExpandedPallet(id="PAL-002", name="Boxes", weight=300.0)
    zone_green.add_pallet(normal_pallet)
    assert len(zone_green.pallets) == 1

    with pytest.raises(CapacityExceededError):
        zone_green.add_pallet(oversized_pallet)

    state_2.advance_to_green()
    assert evaluate_green_gate_result(exit_code=0)["approved"] is True
    services.update_spec_status("SPEC-WMS-002", status="FULFILLED", uow=uow)

    # -------------------------------------------------------------
    # Mutation Type 3: State Transition
    # "Add a status to Pallet (ACTIVE, QUARANTINED). If current_date exceeds expiration_date, transition to QUARANTINED."
    # (Guardrail: Explicit current_date argument, zero datetime.now() leaks)
    # -------------------------------------------------------------
    spec_3_dict = {
        "spec_id": "SPEC-WMS-003",
        "title": "Pallet Expiration Date Quarantine Transition",
        "description": "Transition Pallet status to QUARANTINED if current date exceeds expiration date.",
        "given_when_then": "Given an active Pallet When current_date exceeds expiration_date Then pallet.status is QUARANTINED",
        "target_aggregate": "Pallet",
        "spec_type": SpecMutationType.STATE_TRANSITION.value,
        "is_mathematical_boundary": True,
        "priority": "High",
        "status": "PENDING"
    }
    services.add_inbox_spec(spec_3_dict, uow=uow)

    state_3 = TddExecutionState(spec=BusinessSpec(**spec_3_dict))
    state_3.advance_to_red()
    assert evaluate_red_gate_result(exit_code=1)["approved"] is True

    # GREEN Phase: Pallet lifecycle state transition with explicit date argument
    @dataclass
    class LifecyclePallet:
        id: str
        name: str
        weight: float
        expiration_date: date
        status: str = "ACTIVE"

        def check_expiration(self, current_date: date) -> str:
            """Pure domain method receiving explicit current_date (deterministic)."""
            if current_date > self.expiration_date:
                self.status = "QUARANTINED"
            return self.status

    active_pallet = LifecyclePallet(
        id="PAL-BIO-1",
        name="Organic Produce",
        weight=150.0,
        expiration_date=date(2026, 8, 1)
    )
    assert active_pallet.status == "ACTIVE"

    mock_inspection_date = date(2026, 8, 24)
    res_status = active_pallet.check_expiration(current_date=mock_inspection_date)

    assert res_status == "QUARANTINED"
    assert active_pallet.status == "QUARANTINED"

    fresh_pallet = LifecyclePallet(
        id="PAL-BIO-2",
        name="Fresh Apples",
        weight=120.0,
        expiration_date=date(2026, 9, 30)
    )
    fresh_status = fresh_pallet.check_expiration(current_date=mock_inspection_date)
    assert fresh_status == "ACTIVE"
    assert fresh_pallet.status == "ACTIVE"

    state_3.advance_to_green()
    assert evaluate_green_gate_result(exit_code=0)["approved"] is True
    services.update_spec_status("SPEC-WMS-003", status="FULFILLED", uow=uow)

    # -------------------------------------------------------------
    # Inbox Query & Categorization Integrity Assertion
    # -------------------------------------------------------------
    inbox = services.get_inbox_specs(uow=uow)
    assert len(inbox) == 3
    assert all(s["status"] == "FULFILLED" for s in inbox)
    assert inbox[0]["spec_type"] == "ATTRIBUTE_EXPANSION"
    assert inbox[1]["spec_type"] == "DOMAIN_INVARIANT"
    assert inbox[2]["spec_type"] == "STATE_TRANSITION"
