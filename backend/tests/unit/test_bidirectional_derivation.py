import pytest
from domain.model import RuleCard, CardType
from onboarding.router_engine import (
    derive_logic_rules_from_view_prompt,
    project_ui_affordances_from_logic_card
)

def test_view_to_logic_derivation_creates_logic_card():
    view_name = "ChessBoard"
    prompt = "Add an Undo Move button below the board"
    existing_cards = [
        {"id": "CARD-001", "title": "50-Move Rule", "card_type": "LOGIC", "target": "global"}
    ]
    
    derived_cards = derive_logic_rules_from_view_prompt(
        view_name=view_name,
        prompt=prompt,
        existing_logic_cards=existing_cards
    )
    
    assert len(derived_cards) >= 1
    undo_card = derived_cards[0]
    assert undo_card.card_type == "LOGIC"
    assert "undo" in undo_card.title.lower() or "undo" in undo_card.when_clause.lower() or "ångra" in undo_card.title.lower()
    assert undo_card.derived_from_id == view_name
    assert undo_card.is_active is True

def test_view_to_logic_derivation_skips_pure_styling_prompts():
    view_name = "ChessBoard"
    prompt = "Make the dark tiles deep purple with glowing borders"
    existing_cards = []
    
    derived_cards = derive_logic_rules_from_view_prompt(
        view_name=view_name,
        prompt=prompt,
        existing_logic_cards=existing_cards
    )
    # Pure styling prompts should not synthesize backend logic cards
    assert len(derived_cards) == 0

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
