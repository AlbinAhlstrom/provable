import pytest
from domain.model import RuleCard, CardType
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services

def test_rule_card_model_creation_and_defaults():
    card = RuleCard(
        id="CARD-001",
        title="50-Move Rule",
        card_type=CardType.LOGIC.value,
        target="global",
        description="Offer or declare draw after 50 moves without pawn moves or captures",
        given_clause="50 consecutive moves without pawn moves or captures",
        when_clause="50th move is completed",
        then_clause="Declare draw",
        unless_clause="Checkmate occurs on 50th move"
    )
    assert card.id == "CARD-001"
    assert card.card_type == "LOGIC"
    assert card.target == "global"
    assert card.is_active is True
    assert card.status == "PENDING"
    
    d = card.to_dict()
    assert d["title"] == "50-Move Rule"
    assert d["is_active"] is True
    assert d["card_type"] == "LOGIC"
    assert d["target"] == "global"

def test_add_and_list_cards_in_living_deck():
    uow = FakeUnitOfWork()
    logic_card = RuleCard(
        id="CARD-LOGIC-1",
        title="Bishop Diagonal Movement",
        card_type=CardType.LOGIC.value,
        target="Bishop",
        given_clause="Bishop on square X",
        when_clause="Moved diagonally",
        then_clause="Allow move",
        unless_clause="Path blocked"
    )
    view_card = RuleCard(
        id="CARD-VIEW-1",
        title="Chess Board Grid",
        card_type=CardType.VIEW.value,
        target="ChessBoard",
        description="8x8 alternating dark/light tile grid"
    )
    theme_card = RuleCard(
        id="CARD-THEME-1",
        title="Cyberpunk Theme",
        card_type=CardType.VIEW.value,
        target="global",
        description="Neon blue and violet board tiles with dark slate container"
    )
    
    services.add_rule_card(logic_card, uow=uow)
    services.add_rule_card(view_card, uow=uow)
    services.add_rule_card(theme_card, uow=uow)
    
    deck = services.get_living_deck(uow=uow)
    assert len(deck) == 3
    
    # Assert categorized deck views
    categorized = services.get_categorized_living_deck(uow=uow)
    assert len(categorized["logic_cards"]["global"]) == 0
    assert len(categorized["logic_cards"]["entities"]["Bishop"]) == 1
    assert len(categorized["view_cards"]["global_theme"]) == 1
    assert len(categorized["view_cards"]["components"]["ChessBoard"]) == 1

def test_toggle_rule_card_active_state():
    uow = FakeUnitOfWork()
    card = RuleCard(
        id="CARD-002",
        title="VIP Discount",
        card_type=CardType.LOGIC.value,
        target="Order",
        is_active=True
    )
    services.add_rule_card(card, uow=uow)
    
    # Toggle to Inactive (Paused)
    updated = services.toggle_rule_card("CARD-002", is_active=False, uow=uow)
    assert updated["is_active"] is False
    assert updated["status"] == "PAUSED"
    
    # Toggle back to Active
    updated2 = services.toggle_rule_card("CARD-002", is_active=True, uow=uow)
    assert updated2["is_active"] is True
    assert updated2["status"] == "PENDING"


def test_rule_card_supports_chapter_and_category():
    card = RuleCard(
        id="SPEC-001",
        title="First-Click Safety",
        chapter="Board Setup & Generation",
        category="INVARIANT",
        given_clause="a brand new game",
        when_clause="the player clicks their first tile",
        then_clause="the tile is guaranteed safe"
    )
    assert card.chapter == "Board Setup & Generation"
    assert card.category == "INVARIANT"
    d = card.to_dict()
    assert d["chapter"] == "Board Setup & Generation"
    assert d["category"] == "INVARIANT"


def test_living_deck_groups_by_chapter():
    uow = FakeUnitOfWork()
    c1 = RuleCard(
        id="C-1",
        title="First-Click Safe",
        chapter="Board Setup",
        card_type=CardType.LOGIC.value
    )
    c2 = RuleCard(
        id="C-2",
        title="Difficulty Modes",
        chapter="Board Setup",
        card_type=CardType.LOGIC.value
    )
    c3 = RuleCard(
        id="C-3",
        title="Flag Protection",
        chapter="Flagging & Protection",
        card_type=CardType.LOGIC.value
    )
    services.add_rule_card(c1, uow=uow)
    services.add_rule_card(c2, uow=uow)
    services.add_rule_card(c3, uow=uow)

    chapter_groups = services.get_chapter_grouped_deck(uow=uow)
    assert "Board Setup" in chapter_groups
    assert len(chapter_groups["Board Setup"]) == 2
    assert "Flagging & Protection" in chapter_groups
    assert len(chapter_groups["Flagging & Protection"]) == 1


def test_spec_jargon_cleanliness_verifier():
    from onboarding.router_engine import verify_and_clean_spec_jargon

    jargon_spec = {
        "title": "DigCell Action on GameSession",
        "given_clause": "a GameSession in IN_PROGRESS state",
        "when_clause": "DigCell(x, y) is invoked on TileAggregate",
        "then_clause": "mutate CellState and trigger OCC update"
    }

    clean_spec, violations = verify_and_clean_spec_jargon(jargon_spec)
    assert len(violations) > 0
    # The cleaned spec must not contain low-level programming artifacts
    assert "GameSession" not in clean_spec["given_clause"]
    assert "IN_PROGRESS" not in clean_spec["given_clause"]
    assert "DigCell(x, y)" not in clean_spec["when_clause"]

