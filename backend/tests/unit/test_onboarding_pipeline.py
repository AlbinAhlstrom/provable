import pytest
from domain.model import Requirement, MOCK_DOMAIN_SCHEMA
from service_layer.unit_of_work import FakeUnitOfWork
from onboarding.synthesis import synthesize_application_stack
from onboarding.test_importer import generate_unit_test_for_requirement

def test_synthesize_application_stack_with_fake_uow():
    """
    Given a FakeUnitOfWork and a domain schema
    When synthesize_application_stack is called
    Then synthesized requirements are persisted to uow.requirements and committed.
    """
    uow = FakeUnitOfWork()
    result = synthesize_application_stack(MOCK_DOMAIN_SCHEMA, uow=uow)
    
    assert result["success"] is True
    assert uow.committed is True
    reqs = uow.requirements.list()
    assert len(reqs) > 0
    assert any(r.id.startswith("REQ-") for r in reqs)

def test_generate_unit_test_for_requirement_with_fake_uow():
    """
    Given a FakeUnitOfWork containing a Requirement entity
    When generate_unit_test_for_requirement is called with uow
    Then a test case is added to requirement.tests and committed to uow.
    """
    initial_req = Requirement(
        id="REQ-UNIT-001",
        title="Test Requirement Title",
        description="Test Requirement Description"
    )
    uow = FakeUnitOfWork(initial_requirements=[initial_req])
    
    result = generate_unit_test_for_requirement("REQ-UNIT-001", uow=uow)
    
    assert result["success"] is True
    assert uow.committed is True
    updated_req = uow.requirements.get("REQ-UNIT-001")
    assert len(updated_req.tests) > 0
    assert any(t.get("name") == "test_req_unit_001" for t in updated_req.tests)
