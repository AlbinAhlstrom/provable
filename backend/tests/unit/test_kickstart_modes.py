"""
Unit tests for Dual-Mode Kickstart Engine:
- Fast Mode (0-3 questions)
- Guided Mode (max 5 questions)
- Schema contract for ClarificationQuestion
- Incorporating clarification answers into scaffolding
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from domain.model import KickstartState
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_analyze_kickstart_fast_mode_limits_questions():
    """
    Given a minimal pitch in 'fast' mode
    When analyzing kickstart pitch
    Then clarification questions list is returned and contains between 0 and 3 questions.
    """
    pitch = "Heavy machinery rental fleet with service intervals"
    uow = FakeUnitOfWork()
    res = services.analyze_kickstart_pitch(business_pitch=pitch, mode="fast", uow=uow)
    
    assert res.get("success") is not False
    questions = res.get("clarification_questions", [])
    assert isinstance(questions, list)
    assert len(questions) <= 3
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "options" in q and isinstance(q["options"], list)
        assert "default_choice" in q
        assert "impact_rationale" in q


def test_analyze_kickstart_guided_mode_returns_strategic_forks():
    """
    Given a pitch in 'guided' mode
    When analyzing kickstart pitch
    Then up to 5 strategic domain-fork questions are returned.
    """
    pitch = "Heavy machinery rental fleet with service intervals"
    uow = FakeUnitOfWork()
    res = services.analyze_kickstart_pitch(business_pitch=pitch, mode="guided", uow=uow)
    
    assert res.get("success") is not False
    questions = res.get("clarification_questions", [])
    assert isinstance(questions, list)
    assert len(questions) <= 5
    for q in questions:
        assert "id" in q
        assert "question" in q
        assert "options" in q
        assert "default_choice" in q
        assert "impact_rationale" in q


def test_kickstart_with_clarification_answers():
    """
    Given a pitch and selected clarification answers
    When calling kickstart_domain_and_scaffold
    Then answers are accepted and application stack is synthesized.
    """
    pitch = "Heavy machinery rental fleet with service intervals"
    uow = FakeUnitOfWork()
    answers = {"q_booking_model": "Direct Booking"}
    res = services.kickstart_domain_and_scaffold(
        pitch=pitch,
        answers=answers,
        uow=uow
    )
    assert res.get("success") is True
