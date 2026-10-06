import pytest
from unittest.mock import MagicMock, patch
from onboarding.delta_compiler import (
    classify_delta_specification,
    apply_specification_delta,
    DeltaClassification
)
from domain.model import RuleCard


def test_classify_delta_specification_view_and_logic():
    """Verifies that visual wording (e.g. glow green, theme, highlight) is classified as VIEW/CROSS_CUTTING."""
    view_spec = {
        "title": "Visualize satisfied cells",
        "given_clause": "given an active game",
        "when_clause": "when a numbered tile has an equal amount of flags in adjacent cells",
        "then_clause": "then all of the square's surrounding non-flagged squares glow green",
        "card_type": "LOGIC"
    }
    classification = classify_delta_specification(view_spec)
    assert classification in (DeltaClassification.VIEW, DeltaClassification.CROSS_CUTTING)

    pure_logic_spec = {
        "title": "Mine explosion",
        "given_clause": "an active game",
        "when_clause": "user reveals a mine",
        "then_clause": "session transitions to Defeat state",
        "card_type": "LOGIC"
    }
    logic_classification = classify_delta_specification(pure_logic_spec)
    assert logic_classification == DeltaClassification.LOGIC


@patch("onboarding.delta_compiler._execute_fullstack_delta_evolution")
def test_apply_specification_delta_invokes_evolution(mock_evolve, tmp_path):
    """Verifies that apply_specification_delta triggers the delta evolution graph and updates card status."""
    mock_evolve.return_value = {
        "success": True,
        "files_updated": ["workspace/src/views/SessionView.tsx"],
        "qa_passed": True
    }

    card_data = {
        "id": "CARD-598",
        "title": "Visualize satisfied cells",
        "given_clause": "given an active game",
        "when_clause": "when a numbered tile has an equal amount of flags in adjacent cells",
        "then_clause": "then all surrounding non-flagged squares glow green",
        "card_type": "LOGIC"
    }

    result = apply_specification_delta(card_data, workspace_dir=str(tmp_path), dry_run=False)
    assert result["success"] is True
    assert "SessionView.tsx" in result["files_updated"][0]
    assert result["status"] == "FULFILLED"
