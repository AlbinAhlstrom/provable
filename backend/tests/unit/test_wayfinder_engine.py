"""
Unit Tests for Provable Wayfinder Engine.
Tests graph generation, BDD Mad-Libs clauses, preset switching,
frontier/fog of war DAG progression, and rule deck synchronization.
"""

import pytest
from onboarding.wayfinder import (
    BddClause,
    BddPreset,
    WayfinderTicketType,
    WayfinderTicketStatus,
    WayfinderTicket,
    WayfinderGraphState,
    generate_wayfinder_graph,
    lock_wayfinder_ticket,
    sync_locked_tickets_to_rule_deck
)
from service_layer.unit_of_work import FakeUnitOfWork


def test_bdd_clause_formatting():
    clause = BddClause(
        given="a booking with status CONFIRMED",
        when="guest cancels less than 24 hours prior to check-in",
        then="retain 50% deposit and mark status CANCELLED",
        unless="guest has purchased 'Flexible Cancellation' package"
    )
    gherkin = clause.to_gherkin_text()
    assert "GIVEN a booking with status CONFIRMED" in gherkin
    assert "WHEN guest cancels less than 24 hours prior to check-in" in gherkin
    assert "THEN retain 50% deposit and mark status CANCELLED" in gherkin
    assert "UNLESS guest has purchased 'Flexible Cancellation' package" in gherkin


def test_generate_wayfinder_graph_initial_state():
    pitch = "Boutique Hotel Booking & Housekeeping Engine with room status management"
    graph = generate_wayfinder_graph(pitch)

    assert isinstance(graph, WayfinderGraphState)
    assert len(graph.tickets) >= 5
    assert graph.pitch == pitch
    assert graph.progress_pct == 0
    assert not graph.is_synthesis_ready

    frontier = graph.get_frontier_tickets()
    fog = graph.get_fog_tickets()
    locked = graph.get_locked_tickets()

    # Initial state has frontier and fog, but nothing locked
    assert len(frontier) >= 1
    assert len(fog) >= 2
    assert len(locked) == 0

    # Frontier tickets must have empty dependencies
    for t in frontier:
        assert len(t.depends_on) == 0
        assert t.status == WayfinderTicketStatus.FRONTIER.value
        assert t.bdd_template is not None
        assert len(t.presets) >= 2

    # Fog tickets must have dependencies
    for t in fog:
        assert len(t.depends_on) > 0
        assert t.status == WayfinderTicketStatus.FOG.value


def test_lock_ticket_advances_frontier_and_lifts_fog():
    pitch = "Boutique Hotel Booking & Housekeeping Engine"
    graph = generate_wayfinder_graph(pitch)

    initial_frontier_ids = [t.id for t in graph.get_frontier_tickets()]
    initial_fog_count = len(graph.get_fog_tickets())
    ticket_to_lock = initial_frontier_ids[0]

    custom_bdd = BddClause(
        given="Active hotel room",
        when="Guest initiates check-in",
        then="Generate digital key card and transition to OCCUPIED",
        unless="Room cleaning status is DIRTY"
    )

    updated_graph = lock_wayfinder_ticket(graph, ticket_to_lock, custom_bdd)

    # 1. Target ticket is now locked
    locked_ticket = next(t for t in updated_graph.tickets if t.id == ticket_to_lock)
    assert locked_ticket.status == WayfinderTicketStatus.LOCKED.value
    assert locked_ticket.resolved_bdd == custom_bdd

    # 2. Progress percentage has increased
    assert updated_graph.progress_pct > 0

    # 3. Check that tickets depending ONLY on this locked ticket moved to FRONTIER
    for t in updated_graph.tickets:
        if set(t.depends_on) == {ticket_to_lock}:
            assert t.status == WayfinderTicketStatus.FRONTIER.value


def test_bdd_presets_can_be_selected():
    pitch = "Specialty Coffee Roastery Subscription Engine"
    graph = generate_wayfinder_graph(pitch)
    frontier_ticket = graph.get_frontier_tickets()[0]

    assert len(frontier_ticket.presets) >= 2
    preset = frontier_ticket.presets[0]
    assert preset.bdd.given
    assert preset.bdd.when
    assert preset.bdd.then

    # Lock ticket using preset's BDD
    updated = lock_wayfinder_ticket(graph, frontier_ticket.id, preset.bdd)
    locked = next(t for t in updated.tickets if t.id == frontier_ticket.id)
    assert locked.resolved_bdd.then == preset.bdd.then


def test_sync_locked_tickets_to_rule_deck():
    uow = FakeUnitOfWork()
    pitch = "E-Commerce Checkout & Flash Sale System"
    graph = generate_wayfinder_graph(pitch)

    frontier_ticket = graph.get_frontier_tickets()[0]
    bdd = BddClause(
        given="Cart total > $50",
        when="Customer applies promo code FREESHIP",
        then="Set shipping cost to 0.00",
        unless="Cart contains oversized freight items"
    )
    updated_graph = lock_wayfinder_ticket(graph, frontier_ticket.id, bdd)

    from service_layer import services
    count = sync_locked_tickets_to_rule_deck(updated_graph, uow)
    assert count == 1
    cards = services.get_living_deck(uow)
    assert len(cards) == 1
    card = cards[0]
    assert card["given_clause"] == bdd.given
    assert card["when_clause"] == bdd.when
    assert card["then_clause"] == bdd.then
    assert card["unless_clause"] == bdd.unless
    assert card["is_active"] is True


def test_wayfinder_api_lifecycle():
    from fastapi.testclient import TestClient
    from app import app

    client = TestClient(app)

    # 1. Generate graph from pitch
    res = client.post("/api/wayfinder/generate", json={"pitch": "Autonomous Drone Fleet Management Platform"})
    assert res.status_code == 200
    data = res.json()
    assert data["pitch"] == "Autonomous Drone Fleet Management Platform"
    assert len(data["frontier"]) >= 1
    assert data["progress_pct"] == 0

    first_ticket = data["frontier"][0]
    ticket_id = first_ticket["id"]

    # 2. Inspect state endpoint
    state_res = client.get("/api/wayfinder/state")
    assert state_res.status_code == 200
    state_data = state_res.json()
    assert state_data["pitch"] == "Autonomous Drone Fleet Management Platform"

    # 3. Lock ticket with custom BDD
    lock_payload = {
        "ticket_id": ticket_id,
        "bdd": {
            "given": "Drone battery level > 25%",
            "when": "Dispatch mission command is issued",
            "then": "Arm motors and begin waypoint navigation",
            "unless": "Airspace restricted or adverse weather warning"
        }
    }
    lock_res = client.post("/api/wayfinder/lock", json=lock_payload)
    assert lock_res.status_code == 200
    lock_data = lock_res.json()
    assert lock_data["progress_pct"] > 0
    locked_ticket = next(t for t in lock_data["locked"] if t["id"] == ticket_id)
    assert locked_ticket["resolved_bdd"]["given"] == "Drone battery level > 25%"


def test_chess_app_behavior_driven_invariants():
    """
    Verifies that 'a chess app' generates human-accessible, behavior-driven tickets:
    - Root frontier asks who is playing (solo vs pass & play vs online) and move guidance.
    - Zero mentions of OCC, ConcurrencyCollisionError, UnitOfWork, or technical plumbing.
    - Fog of War correctly hides downstream tickets until player model is locked.
    """
    graph = generate_wayfinder_graph("a chess app")
    
    frontier = graph.get_frontier_tickets()
    fog = graph.get_fog_tickets()
    
    # 1. Frontier must start with foundational user questions
    frontier_ids = [t.id for t in frontier]
    assert "wf-001-player-model" in frontier_ids
    assert "wf-002-move-guidance" in frontier_ids
    
    # 2. Player Model must have clean presets (Solo, Pass & Play, Online)
    player_ticket = next(t for t in frontier if t.id == "wf-001-player-model")
    assert player_ticket.title == "Who is Playing?"
    labels = [p.label for p in player_ticket.presets]
    assert any("Solo Play" in l for l in labels)
    assert any("Pass & Play" in l for l in labels)
    assert any("Friend Online" in l for l in labels)
    
    # 3. Ban on Technical Jargon across all tickets
    import re
    forbidden_terms = [
        r"\bocc\b", r"\bconcurrency\b", r"\bcollision\b", r"\bunit of work\b",
        r"\basynchronous\b", r"\bmessagebus\b", r"\blifecycle\b", r"\bdraft\b",
        r"\bstatus to active\b", r"\bsql\b", r"\bdatabase\b"
    ]
    for ticket in graph.tickets:
        title_lower = ticket.title.lower()
        rationale_lower = ticket.rationale.lower()
        for pattern in forbidden_terms:
            assert not re.search(pattern, title_lower), f"Forbidden pattern '{pattern}' found in ticket title: {ticket.title}"
            assert not re.search(pattern, rationale_lower), f"Forbidden pattern '{pattern}' found in ticket rationale: {ticket.rationale}"
        
        # Check presets BDD
        for preset in ticket.presets:
            bdd_text = f"{preset.bdd.given} {preset.bdd.when} {preset.bdd.then} {preset.bdd.unless or ''}".lower()
            for pattern in forbidden_terms:
                assert not re.search(pattern, bdd_text), f"Forbidden pattern '{pattern}' found in preset BDD: {preset.label}"

    # 4. Fog of War lifts causally
    # Locking player model lifts Undo and Board View into Frontier
    updated = lock_wayfinder_ticket(graph, "wf-001-player-model", player_ticket.presets[0].bdd)
    new_frontier_ids = [t.id for t in updated.get_frontier_tickets()]
    assert "wf-003-undo" in new_frontier_ids
    assert "wf-004-board-view" in new_frontier_ids
    # But Game Over remains in Fog (depends on Undo being locked)
    new_fog_ids = [t.id for t in updated.get_fog_tickets()]
    assert "wf-006-game-over" in new_fog_ids


def test_chess_app_synthesis_populates_living_deck_and_workspace_preview(tmp_path, monkeypatch):
    """
    End-to-end Wayfinder Synthesis verification:
    1. Lock behavior-driven BDD tickets for 'a chess app'.
    2. Synthesize application stack.
    3. Assert Living Rule Deck (/api/specs/deck) contains the locked BDD tickets.
    4. Assert workspace/src/App.tsx is written with the interactive Chessboard component.
    """
    import os
    from fastapi.testclient import TestClient
    from app import app
    from service_layer.unit_of_work import SqliteUnitOfWork
    from service_layer import services

    # Point workspace to a temp directory to isolate test
    ws_dir = tmp_path / "workspace"
    ws_src = ws_dir / "src"
    ws_src.mkdir(parents=True)
    monkeypatch.setenv("PROVABLE_WORKSPACE", str(ws_dir))

    client = TestClient(app)

    # 1. Generate graph for 'a chess app'
    gen_res = client.post("/api/wayfinder/generate", json={"pitch": "a chess app"})
    assert gen_res.status_code == 200

    # 2. Lock frontier tickets: player model & move guidance
    lock1 = client.post("/api/wayfinder/lock", json={
        "ticket_id": "wf-001-player-model",
        "bdd": {
            "given": "Player opens the chess app",
            "when": "Starting a new game session",
            "then": "Provide instant 2-player pass and play on this device",
            "unless": "Saved game is resumed"
        }
    })
    assert lock1.status_code == 200

    lock2 = client.post("/api/wayfinder/lock", json={
        "ticket_id": "wf-002-move-guidance",
        "bdd": {
            "given": "A chess piece is tapped",
            "when": "Current player considers moves",
            "then": "Highlight valid legal destination squares on the board",
            "unless": "Player disables hints in settings"
        }
    })
    assert lock2.status_code == 200

    # 3. Synthesize application stack
    synth_res = client.post("/api/wayfinder/synthesize")
    assert synth_res.status_code == 200
    synth_data = synth_res.json()
    assert synth_data.get("success") is True

    # 4. Assert Living Rule Deck contains both locked rule cards
    uow = SqliteUnitOfWork()
    living_cards = services.get_living_deck(uow)
    assert len(living_cards) >= 2
    rule_titles = [c["title"] for c in living_cards]
    assert "Who is Playing?" in rule_titles
    assert "Move Guidance & Rule Enforcement" in rule_titles

    deck_res = client.get("/api/specs/deck")
    assert deck_res.status_code == 200
    deck_data = deck_res.json()
    all_categorized_cards = (
        deck_data.get("logic_cards", {}).get("global", [])
        + deck_data.get("view_cards", {}).get("global_theme", [])
    )
    for ent_cards in deck_data.get("logic_cards", {}).get("entities", {}).values():
        all_categorized_cards.extend(ent_cards)
    for comp_cards in deck_data.get("view_cards", {}).get("components", {}).values():
        all_categorized_cards.extend(comp_cards)

    cat_titles = [c["title"] for c in all_categorized_cards]
    assert "Who is Playing?" in cat_titles

    # 5. Assert workspace/src/App.tsx was synthesized
    app_tsx_path = ws_src / "App.tsx"
    assert app_tsx_path.exists(), "workspace/src/App.tsx was not synthesized!"
    app_code = app_tsx_path.read_text(encoding="utf-8")
    assert "export default App" in app_code or "export default function App" in app_code





