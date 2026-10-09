"""An entity that only exists inside another is stored inside its owner (backend/onboarding/owned_parts.py).

A game whose squares are a separate collection has no board: its methods and its rules see the turn and nothing else.
The decomposition already says which entities are parts (not an aggregate root, related to one root); the generated
aggregate now holds them, so its behaviour can read and change them.
"""
import json
import subprocess
import sys

from onboarding.owned_parts import embed_owned_parts
from onboarding.router_engine import AudienceRole, BusinessSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton
from service_layer.tdd_machine import summarize_class_api


def _structure():
    return DomainStructureSchema(domain_name="Chess", entities=[
        EntitySpec(name="GameSession", audience_role=AudienceRole.CREATED,
                   attributes=[{"name": "id", "type": "string"}, {"name": "turn_color", "type": "string", "default_value": "white"}],
                   relationships=[{"target": "BoardSquare", "relation_type": "one_to_many"}]),
        EntitySpec(name="BoardSquare", is_aggregate_root=False, audience_role=AudienceRole.CREATED,
                   attributes=[{"name": "id", "type": "string"}, {"name": "game_session_id", "type": "string"},
                               {"name": "coordinate", "type": "string"}, {"name": "move_count", "type": "int"}],
                   relationships=[{"target": "GameSession", "relation_type": "many_to_one"}]),
        EntitySpec(name="Player", audience_role=AudienceRole.CREATED, attributes=[{"name": "id", "type": "string"}]),
    ])


def _spec(target):
    return BusinessSpec(spec_id="SPEC-001", title="t", description="d", given_when_then="Given a When b Then c", target_aggregate=target)


def test_a_part_becomes_a_list_its_owner_holds():
    """Verify the part leaves the list of stored entities and its owner gains a typed list of it.

    id: TST-PART-001
    Given: A root related one-to-many to an entity that is not an aggregate root, and a spec targeting that entity
    When: Owned parts are embedded
    Then: Only the roots remain; the owner has a list attribute describing one item (without the key back to its
          owner); the spec now targets the owner
    """
    structure, specs = _structure(), [_spec("BoardSquare")]
    owners = embed_owned_parts(structure, specs)

    assert owners == {"BoardSquare": "GameSession"}
    assert [e.name for e in structure.entities] == ["GameSession", "Player"]
    squares = next(a for a in structure.entities[0].attributes if a.name == "board_squares")
    assert squares.item_name == "BoardSquare" and [a.name for a in squares.item_attributes] == ["id", "coordinate", "move_count"]
    assert squares.describe() == "board_squares: list of BoardSquare {id: string, coordinate: string, move_count: int}"
    assert specs[0].target_aggregate == "GameSession"


def test_an_entity_with_no_single_owner_stays_its_own_collection():
    """Verify nothing is embedded unless exactly one root owns the part.

    id: TST-PART-002
    Given: A non-root entity related to two roots, and a root related to another root
    When: Owned parts are embedded
    Then: Every entity is still stored on its own
    """
    structure = DomainStructureSchema(domain_name="Salon", entities=[
        EntitySpec(name="Stylist", attributes=[{"name": "id", "type": "string"}],
                   relationships=[{"target": "Appointment", "relation_type": "one_to_many"}]),
        EntitySpec(name="Service", attributes=[{"name": "id", "type": "string"}]),
        EntitySpec(name="Slot", is_aggregate_root=False, attributes=[{"name": "id", "type": "string"}],
                   relationships=[{"target": "Stylist", "relation_type": "many_to_one"}, {"target": "Service", "relation_type": "many_to_one"}]),
        EntitySpec(name="Appointment", attributes=[{"name": "id", "type": "string"}]),
    ])
    assert embed_owned_parts(structure, []) == {}
    assert [e.name for e in structure.entities] == ["Stylist", "Service", "Slot", "Appointment"]


def test_the_generated_aggregate_holds_serves_and_documents_its_parts(tmp_path):
    """Verify the skeleton writes the owner with its parts inside, end to end through the generated API.

    id: TST-PART-003
    Given: A structure whose squares were embedded in the game session
    When: The skeleton is written and a session with one square is created through its API
    Then: The part has no module, router or client of its own; the session is stored and served with its square, and
          with a field that was added to the object later; the class and the client describe one item's keys
    """
    structure = _structure()
    embed_owned_parts(structure, [])
    build_and_write_skeleton(structure, target_dir=str(tmp_path))

    assert not (tmp_path / "src" / "domain" / "board_square.py").exists()
    assert not (tmp_path / "src" / "entrypoints" / "routers" / "board_square.py").exists()
    domain = (tmp_path / "src" / "domain" / "game_session.py").read_text(encoding="utf-8")
    assert "board_squares: List[Dict[str, Any]] = field(default_factory=list)" in domain
    api = summarize_class_api(domain[domain.index("@dataclass"):])
    assert "BoardSquare" in api and "coordinate" in api  # the test writer is shown what one item holds
    client = (tmp_path / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    assert "board_squares?: Array<{ id: string; coordinate: string; move_count: number }>" in client

    script = ("from fastapi.testclient import TestClient\nfrom src.app import app\nimport json\nc = TestClient(app)\n"
              "made = c.post('/api/game_sessions', json={'board_squares': [{'id': 'a1', 'coordinate': 'a1', 'move_count': 0}]})\n"
              "from src.entrypoints.routers import game_session as r\n"
              "r._uow.game_sessions.get(made.json()['id']).selected_square = 'a1'\n"
              "print(json.dumps([made.status_code, c.get('/api/game_sessions').json()]))")
    out = subprocess.run([sys.executable, "-c", script], cwd=tmp_path, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    status, sessions = json.loads(out.stdout.strip().splitlines()[-1])
    assert status == 201 and sessions[0]["board_squares"] == [{"id": "a1", "coordinate": "a1", "move_count": 0}]
    assert sessions[0]["selected_square"] == "a1"  # a field the domain grew later is served, not filtered away


def _nested():
    return DomainStructureSchema(domain_name="Orders", entities=[
        EntitySpec(name="Order", audience_role=AudienceRole.CREATED,
                   attributes=[{"name": "id", "type": "string"}, {"name": "status", "type": "string"}]),
        EntitySpec(name="Parcel", is_aggregate_root=False,
                   attributes=[{"name": "id", "type": "string"}, {"name": "order_id", "type": "string"},
                               {"name": "weight", "type": "float"}],
                   relationships=[{"target": "Order", "relation_type": "many_to_one"}]),
        EntitySpec(name="ParcelItem", is_aggregate_root=False,
                   attributes=[{"name": "id", "type": "string"}, {"name": "parcel_id", "type": "string"},
                               {"name": "quantity", "type": "int"}],
                   relationships=[{"target": "Parcel", "relation_type": "many_to_one"}]),
    ])


def test_a_part_of_a_part_is_stored_inside_it():
    """Verify ownership is followed all the way down: where a part's own parts live is decided, not left open.

    id: TST-PART-004
    Given: A root that owns a part, which in turn owns a part of its own (the items of a parcel of an order, the
           cells of a board of a game), and a spec targeting the innermost
    When: Owned parts are embedded
    Then: Only the root remains; its part list describes one item, which holds the list of its own parts with their
          keys (without the key back to their owner); the spec targets the root
    """
    structure, specs = _nested(), [_spec("ParcelItem")]
    owners = embed_owned_parts(structure, specs)

    assert owners == {"Parcel": "Order", "ParcelItem": "Order"}
    assert [e.name for e in structure.entities] == ["Order"]
    parcels = next(a for a in structure.entities[0].attributes if a.name == "parcels")
    assert [a.name for a in parcels.item_attributes] == ["id", "weight", "parcel_items"]
    assert parcels.describe() == ("parcels: list of Parcel {id: string, weight: float, "
                                  "parcel_items: list of ParcelItem {id: string, quantity: int}}")
    assert specs[0].target_aggregate == "Order"


def test_a_part_whose_owner_is_stored_on_its_own_stays_a_collection():
    """Verify a part is only nested when the chain of owners ends in an aggregate root.

    id: TST-PART-005
    Given: A non-root entity that belongs to another non-root entity, which belongs to two roots
    When: Owned parts are embedded
    Then: Both stay stored on their own
    """
    structure = DomainStructureSchema(domain_name="Salon", entities=[
        EntitySpec(name="Stylist", attributes=[{"name": "id", "type": "string"}]),
        EntitySpec(name="Service", attributes=[{"name": "id", "type": "string"}]),
        EntitySpec(name="Slot", is_aggregate_root=False, attributes=[{"name": "id", "type": "string"}],
                   relationships=[{"target": "Stylist", "relation_type": "many_to_one"}, {"target": "Service", "relation_type": "many_to_one"}]),
        EntitySpec(name="Note", is_aggregate_root=False, attributes=[{"name": "id", "type": "string"}],
                   relationships=[{"target": "Slot", "relation_type": "many_to_one"}]),
    ])
    assert embed_owned_parts(structure, []) == {}
    assert [e.name for e in structure.entities] == ["Stylist", "Service", "Slot", "Note"]


def test_the_generated_class_and_client_state_the_nested_parts(tmp_path):
    """Verify everyone who writes against the class is shown the same nested shape.

    id: TST-PART-006
    Given: A structure whose parcels, with their items, were embedded in the order
    When: The skeleton is written
    Then: Neither part has a module of its own; the class's description and the client's type state what one parcel
          holds, including the keys of its items
    """
    structure = _nested()
    embed_owned_parts(structure, [])
    build_and_write_skeleton(structure, target_dir=str(tmp_path))

    assert not (tmp_path / "src" / "domain" / "parcel.py").exists()
    assert not (tmp_path / "src" / "domain" / "parcel_item.py").exists()
    domain = (tmp_path / "src" / "domain" / "order.py").read_text(encoding="utf-8")
    assert ("parcels: the Parcel records this Order owns, one dict each with the keys id (str), weight (float), "
            "parcel_items (a list of the ParcelItem records it owns, one dict each with the keys id (str), quantity (int)).") in domain
    client = (tmp_path / "src" / "api" / "client.ts").read_text(encoding="utf-8")
    assert "parcels?: Array<{ id: string; weight: number; parcel_items: Array<{ id: string; quantity: number }> }>" in client
