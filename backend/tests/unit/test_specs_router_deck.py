import pytest
from fastapi.testclient import TestClient
from app import app
from service_layer.unit_of_work import FakeUnitOfWork
from domain.model import RuleCard, CardType
from service_layer import services

client = TestClient(app)

def test_deck_api_endpoints_crud(monkeypatch):
    fake_uow = FakeUnitOfWork()
    
    # Patch SqliteUnitOfWork in specs router to use our fake_uow
    monkeypatch.setattr("entrypoints.routers.specs.SqliteUnitOfWork", lambda: fake_uow)
    
    # 1. Add Logic Card
    resp1 = client.post("/api/specs/deck/add", json={
        "id": "CARD-001",
        "title": "50-Move Rule",
        "card_type": "LOGIC",
        "target": "global",
        "given_clause": "50 moves without capture",
        "when_clause": "50th move is played",
        "then_clause": "Offer draw"
    })
    assert resp1.status_code == 201
    data1 = resp1.json()
    assert data1["success"] is True
    assert data1["card"]["id"] == "CARD-001"
    assert data1["card"]["target"] == "global"
    assert data1["card"]["is_active"] is True
    
    # 2. Add View Card
    resp2 = client.post("/api/specs/deck/add", json={
        "id": "CARD-002",
        "title": "Chess Board View",
        "card_type": "VIEW",
        "target": "ChessBoard",
        "description": "Interactive board"
    })
    assert resp2.status_code == 201
    
    # 3. Get Living Deck
    resp3 = client.get("/api/specs/deck")
    assert resp3.status_code == 200
    deck = resp3.json()
    assert "logic_cards" in deck
    assert "view_cards" in deck
    assert len(deck["logic_cards"]["global"]) == 1
    assert len(deck["view_cards"]["components"]["ChessBoard"]) == 1
    
    # 4. Toggle Card Active State
    resp4 = client.post("/api/specs/deck/CARD-001/toggle", json={"is_active": False})
    assert resp4.status_code == 200
    toggled = resp4.json()
    assert toggled["card"]["is_active"] is False
    assert toggled["card"]["status"] == "PAUSED"
    
    # 5. Update Card
    resp5 = client.post("/api/specs/deck/CARD-001/update", json={"title": "Updated 50-Move Rule"})
    assert resp5.status_code == 200
    updated = resp5.json()
    assert updated["card"]["title"] == "Updated 50-Move Rule"

    # 6. Delete Card
    resp6 = client.delete("/api/specs/deck/CARD-001")
    assert resp6.status_code == 200
    assert resp6.json()["success"] is True

    # 7. Verify Deleted
    resp7 = client.get("/api/specs/deck")
    assert resp7.status_code == 200
    deck7 = resp7.json()
    assert len(deck7["logic_cards"]["global"]) == 0



def test_a_rules_page_test_is_run_through_the_api(monkeypatch):
    """
    Given: A deck with one rule and a prover that says the rule fails
    When: POST /api/specs/rules/{id}/test is called, then for an unknown rule, then for the whole deck
    Then: The first answers the verdict and the deck shows a red light; the second is 404; the third counts one fail
    """
    from service_layer import rule_tests
    fake_uow = FakeUnitOfWork()
    monkeypatch.setattr("entrypoints.routers.specs.SqliteUnitOfWork", lambda: fake_uow)
    services.add_rule_card({"id": "SPEC-001", "title": "A rule", "card_type": "LOGIC", "target": "global",
                            "given_clause": "a", "when_clause": "b", "then_clause": "c", "is_active": True}, uow=fake_uow)

    def prover(rule, workspace_dir, page_url, stored=None, app=None, plan=""):
        return {"status": "fail", "reason": "AssertionError: nothing happened", "evidence": "", "source": "s",
                "written_for": "x", "written": 1}
    monkeypatch.setattr(rule_tests.page_tests, "prove_rule", prover)
    monkeypatch.setattr(rule_tests.page_tests, "describe_app", lambda ws, url, plan="": None)

    one = client.post("/api/specs/rules/SPEC-001/test")
    assert one.status_code == 200 and one.json()["status"] == "fail" and one.json()["success"] is False
    card = client.get("/api/specs/deck").json()["all_cards"][0]
    assert (card["test_status"], card["test_reason"]) == ("fail", "AssertionError: nothing happened")
    assert client.post("/api/specs/rules/SPEC-404/test").status_code == 404
    assert client.post("/api/specs/rules/test").json()["counts"] == {"pass": 0, "fail": 1, "broken": 0}
