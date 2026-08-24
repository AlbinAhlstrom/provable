import pytest
from onboarding.router_engine import BusinessSpec, DomainBehaviorInboxSchema
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services

def test_add_and_list_specs_service():
    uow = FakeUnitOfWork()
    spec = BusinessSpec(
        spec_id="SPEC-101",
        title="Enforce Maximum Pallet Load",
        description="Pallets cannot exceed 1200kg.",
        given_when_then="Given pallet over 1200kg When validating Then raise OverloadException",
        target_aggregate="Pallet",
        is_mathematical_boundary=True
    )
    
    # Add spec
    added_spec = services.add_inbox_spec(spec, uow=uow)
    assert added_spec.spec_id == "SPEC-101"
    
    # List specs
    inbox = services.get_inbox_specs(uow=uow)
    assert any(s["spec_id"] == "SPEC-101" for s in inbox)

def test_update_spec_status_service():
    uow = FakeUnitOfWork()
    spec = BusinessSpec(
        spec_id="SPEC-102",
        title="FIFO Dispatch Sequence",
        description="Oldest batches are dispatched first.",
        given_when_then="Given batches When ordering Then oldest batch is first",
        target_aggregate="Warehouse"
    )
    services.add_inbox_spec(spec, uow=uow)
    
    # Update status to FULFILLED
    updated = services.update_spec_status("SPEC-102", status="FULFILLED", uow=uow)
    assert updated["status"] == "FULFILLED"
    
    # Verify in list
    inbox = services.get_inbox_specs(uow=uow)
    target = next(s for s in inbox if s["spec_id"] == "SPEC-102")
    assert target["status"] == "FULFILLED"
