"""
High-Gear TDD Unit Tests for Service Layer & Unit of Work with Fakes.
Defines service layer use-cases using FakeRepository & FakeUnitOfWork before implementation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def test_add_requirement_service():
    """
    Given a FakeUnitOfWork
    When executing add_requirement service workflow
    Then requirement is added to FakeRepository and transaction is committed.
    """
    from service_layer.unit_of_work import FakeUnitOfWork
    from service_layer import services

    uow = FakeUnitOfWork()
    req = services.create_requirement(
        req_id="REQ-100",
        title="Payment Gateway Integration",
        description="Support credit card checkout",
        uow=uow
    )

    assert req.id == "REQ-100"
    assert uow.requirements.get("REQ-100") is not None
    assert uow.committed is True


def test_get_requirement_service_not_found_raises():
    """
    Given an empty FakeUnitOfWork
    When attempting to fetch non-existent requirement
    Then RequirementNotFound exception is raised.
    """
    from service_layer.unit_of_work import FakeUnitOfWork
    from service_layer import services, exceptions

    uow = FakeUnitOfWork()
    with pytest.raises(exceptions.RequirementNotFound):
        services.get_requirement("REQ-999", uow=uow)
