"""
Unit tests for Reviews service workflows using FakeUnitOfWork.
Tests code review fetching, feedback submission, approval, and rejection.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import Requirement
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services, exceptions


def test_get_code_reviews():
    """
    Given a FakeUnitOfWork containing requirements in 'Review' and 'Backlog' statuses
    When calling get_code_reviews service workflow
    Then only requirements with status 'Review' are returned.
    """
    r1 = Requirement(
        id="REQ-REV-001",
        title="Review Req 1",
        description="Desc 1",
        status="Review",
        proposed_code="print('hello')",
        feedback="Looks good initial"
    )
    r2 = Requirement(
        id="REQ-REV-002",
        title="Backlog Req 2",
        description="Desc 2",
        status="Backlog"
    )
    uow = FakeUnitOfWork(initial_requirements=[r1, r2])

    reviews = services.get_code_reviews(uow=uow)

    assert len(reviews) == 1
    assert reviews[0]["id"] == "REQ-REV-001"
    assert reviews[0]["title"] == "Review Req 1"
    assert reviews[0]["proposedCode"] == "print('hello')"
    assert reviews[0]["feedback"] == "Looks good initial"


def test_approve_code_service():
    """
    Given a FakeUnitOfWork containing a requirement in 'Review' status
    When calling approve_code service workflow
    Then requirement status transitions to 'Test' and UoW is committed.
    """
    r = Requirement(
        id="REQ-REV-003",
        title="Review Req 3",
        description="Desc 3",
        status="Review"
    )
    uow = FakeUnitOfWork(initial_requirements=[r])

    approved = services.approve_code(req_id="REQ-REV-003", uow=uow)

    assert approved.status == "Test"
    saved = uow.requirements.get("REQ-REV-003")
    assert saved is not None
    assert saved.status == "Test"
    assert uow.committed is True


def test_reject_code_service():
    """
    Given a FakeUnitOfWork containing a requirement in 'Review' status
    When calling reject_code service workflow with feedback
    Then requirement status transitions to 'In_Progress', feedback is saved, and UoW is committed.
    """
    r = Requirement(
        id="REQ-REV-004",
        title="Review Req 4",
        description="Desc 4",
        status="Review"
    )
    uow = FakeUnitOfWork(initial_requirements=[r])

    rejected = services.reject_code(
        req_id="REQ-REV-004",
        feedback="Please fix component alignment and rerun tests.",
        uow=uow
    )

    assert rejected.status == "In_Progress"
    assert rejected.feedback == "Please fix component alignment and rerun tests."
    saved = uow.requirements.get("REQ-REV-004")
    assert saved is not None
    assert saved.status == "In_Progress"
    assert saved.feedback == "Please fix component alignment and rerun tests."
    assert uow.committed is True


def test_submit_review_feedback_service():
    """
    Given a FakeUnitOfWork containing a requirement
    When calling submit_review_feedback service workflow
    Then feedback field is updated and UoW is committed.
    """
    r = Requirement(
        id="REQ-REV-005",
        title="Review Req 5",
        description="Desc 5",
        status="Review"
    )
    uow = FakeUnitOfWork(initial_requirements=[r])

    updated = services.submit_review_feedback(
        req_id="REQ-REV-005",
        feedback="Initial code review feedback noted.",
        uow=uow
    )

    assert updated.feedback == "Initial code review feedback noted."
    saved = uow.requirements.get("REQ-REV-005")
    assert saved is not None
    assert saved.feedback == "Initial code review feedback noted."
    assert uow.committed is True
