"""The rule deck a kickstart starts with: one card for each rule of the product, in a person's words."""

from onboarding.router_engine import BusinessSpec, SpecKind
from onboarding.rule_deck import clauses_of, deck_cards


def _spec(number, **fields):
    return BusinessSpec(**{"spec_id": f"SPEC-{number:03d}", "title": f"Rule {number}", "description": "what is seen",
                           "given_when_then": "Given order_sent, When add_line(item 'soup'), Then OrderLockedError",
                           "target_aggregate": "Order", **fields})


def test_the_deck_holds_one_card_for_each_rule_and_nothing_else():
    """Verify the deck is the product's own rules: no card is added that no rule stands behind.

    id: TST-DECK-001
    Given: Three specs of a product
    When: The deck's cards are made
    Then: There are three cards, in the specs' order and under their ids, every one active
    """
    cards = deck_cards([_spec(1), _spec(2), _spec(3)], master_name="Order")

    assert [card["id"] for card in cards] == ["SPEC-001", "SPEC-002", "SPEC-003"]
    assert all(card["is_active"] and card["status"] == "ACTIVE" and card["target"] == "Order" for card in cards)


def test_a_card_says_the_rule_as_a_person_would():
    """Verify what a person reads on a card is the rule's plain wording, not the line its tests are written from.

    id: TST-DECK-002
    Given: A spec with an exact line in the contract's names and a plain wording beside it
    When: Its card is made
    Then: The card's Given, When and Then are the plain wording's, and no action or situation name is on the card
    """
    card = deck_cards([_spec(1, plain="Given an order that was sent, When a guest adds a dish, Then they are told "
                                      "it can no longer be changed.")], master_name="Order")[0]

    assert card["given_clause"] == "an order that was sent"
    assert card["when_clause"] == "a guest adds a dish"
    assert card["then_clause"] == "they are told it can no longer be changed."
    assert not any("add_line" in str(value) or "order_sent" in str(value) for value in card.values())


def test_a_rule_without_a_plain_wording_is_shown_by_its_only_one():
    """Verify a rule that has one wording (one a person wrote, or one from the earlier front) is still a card.

    id: TST-DECK-003
    Given: A spec with no plain wording
    When: Its card is made
    Then: The card's clauses are those of its Given, When, Then line
    """
    card = deck_cards([_spec(1)], master_name="Order")[0]

    assert (card["given_clause"], card["when_clause"], card["then_clause"]) == (
        "order_sent", "add_line(item 'soup')", "OrderLockedError")


def test_a_rule_of_the_page_alone_is_a_card_of_the_page():
    """Verify the deck tells a rule the records obey from one of the page alone, as the contract does.

    id: TST-DECK-004
    Given: A behaviour spec that states a limit and a presentation spec
    When: Their cards are made
    Then: The first is a logic card marked as a calculation, the second a view card
    """
    logic, view = deck_cards([_spec(1, is_mathematical_boundary=True, category=None),
                              _spec(2, kind=SpecKind.PRESENTATION.value, category=None)], master_name="Order")

    assert (logic["card_type"], logic["category"]) == ("LOGIC", "CALCULATION")
    assert view["card_type"] == "VIEW"


def test_clauses_are_read_from_a_line_in_any_case_and_with_an_unless():
    """Verify a Given/When/Then line is split at its keywords however they are written.

    id: TST-DECK-005
    Given: A line with lower-case keywords and an Unless
    When: Its clauses are read
    Then: Each clause holds its own words
    """
    assert clauses_of("given a free table when it is booked then it is taken unless it is closed") == {
        "given_clause": "a free table", "when_clause": "it is booked", "then_clause": "it is taken",
        "unless_clause": "it is closed"}
