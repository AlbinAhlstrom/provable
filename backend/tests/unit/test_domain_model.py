"""
Low-Gear TDD Unit Tests for Provable Domain Entities & Invariants.
Defines entity behaviors and invariants BEFORE production implementation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def test_requirement_identity_equality():
    """
    Given two Requirement domain entities with identical IDs
    When evaluating equality
    Then they are equal regardless of title or status changes.
    """
    from domain.model import Requirement
    r1 = Requirement(id="REQ-001", title="Feature A", description="Desc A", status="Backlog")
    r2 = Requirement(id="REQ-001", title="Feature A Modified", description="Desc B", status="Done")
    assert r1 == r2
    assert hash(r1) == hash(r2)


def test_requirement_status_transition_valid():
    """
    Given a Requirement in Backlog status
    When transitioning status to In_Progress
    Then the status updates correctly.
    """
    from domain.model import Requirement
    r = Requirement(id="REQ-002", title="Feature B", description="Desc B", status="Backlog")
    r.start_progress()
    assert r.status == "In_Progress"


def test_requirement_invalid_status_transition_raises():
    """
    Given a Requirement in Backlog status
    When trying to transition directly to Done without passing Review/Test
    Then an InvalidStatusTransition domain exception is raised.
    """
    from domain.model import Requirement, InvalidStatusTransition
    r = Requirement(id="REQ-003", title="Feature C", description="Desc C", status="Backlog")
    with pytest.raises(InvalidStatusTransition):
        r.complete()
