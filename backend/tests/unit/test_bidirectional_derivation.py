import pytest
from domain.model import RuleCard, CardType
from onboarding.router_engine import project_ui_affordances_from_logic_card

def test_logic_to_view_projection_identifies_ui_affordances():
    logic_card = RuleCard(
        id="CARD-CLOCK",
        title="5-Minute Blitz Clock",
        card_type=CardType.LOGIC.value,
        target="global",
        description="Tracks 5-minute countdown for active player",
        given_clause="Match starts",
        when_clause="Player makes a move",
        then_clause="Switch active timer countdown",
        unless_clause="Timer reaches 00:00"
    )
    existing_view_cards = [
        {"id": "VIEW-1", "title": "Chess Board View", "card_type": "VIEW", "target": "ChessBoard"}
    ]
    
    projections = project_ui_affordances_from_logic_card(
        card=logic_card,
        existing_view_cards=existing_view_cards
    )
    
    assert len(projections) >= 1
    proj = projections[0]
    assert proj["target_view"] == "ChessBoard"
    assert "affordance_type" in proj  # e.g., "timer_display", "action_button", "input_field"
