"""
Unit tests for Autonomous Kickstart Engine (0-question flow).
Verifies that pitch analysis extracts capability blocks and domain requirements cleanly
without prompting the user with clarification questionnaires.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from domain.model import KickstartState
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_analyze_kickstart_pitch_extracts_blocks_and_requirements():
    """
    Given a minimal business pitch
    When analyzing kickstart pitch
    Then capability blocks and domain requirements are extracted without questions.
    """
    pitch = "Heavy machinery rental fleet with service intervals"
    uow = FakeUnitOfWork()
    res = services.analyze_kickstart_pitch(business_pitch=pitch, uow=uow)

    assert res.get("success") is True
    assert "blocks" in res
    assert isinstance(res["blocks"], list)
    assert len(res["blocks"]) > 0
    assert "extracted_requirements" in res
    assert isinstance(res["extracted_requirements"], list)
    assert len(res["extracted_requirements"]) > 0


def test_kickstart_autonomous_scaffolding():
    """
    Given a natural language business pitch
    When calling kickstart_domain_and_scaffold
    Then application stack is synthesized synchronously.
    """
    pitch = "Heavy machinery rental fleet with service intervals"
    uow = FakeUnitOfWork()
    res = services.kickstart_domain_and_scaffold(
        pitch=pitch,
        uow=uow
    )
    assert res.get("success") is True
    assert "aggregates" in res
    assert len(res["created_files"]) > 0
