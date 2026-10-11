"""The generated API exposes verified domain methods through one deterministic action endpoint (the WIRE step)."""

import os
import subprocess
import sys
import textwrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding.router_engine import AttributeSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

CLIENT_SCRIPT = textwrap.dedent('''
    import json, sys
    from fastapi.testclient import TestClient
    from src.app import app

    c = TestClient(app)
    out = {}
    out["created"] = c.post("/api/widgets", json={"id": "w1", "label": "first"}).status_code
    ok = c.post("/api/widgets/w1/action", json={"action_type": " Rename ", "params": {"new_label": "second"}})
    out["rename"] = [ok.status_code, ok.json()]
    out["state_persisted"] = c.get("/api/widgets/w1").json()["label"]
    bad = c.post("/api/widgets/w1/action", json={"action_type": "rename", "params": {"new_label": ""}})
    out["domain_error"] = [bad.status_code, bad.json()]
    out["unknown"] = [c.post("/api/widgets/w1/action", json={"action_type": "explode"}).status_code]
    out["missing_entity"] = c.post("/api/widgets/nope/action", json={"action_type": "rename"}).status_code
    out["bad_params"] = c.post("/api/widgets/w1/action", json={"action_type": "rename", "params": {"wrong": 1}}).status_code
    out["private"] = c.post("/api/widgets/w1/action", json={"action_type": "to_dict"}).status_code
    print("RESULT=" + json.dumps(out))
''')


def test_action_endpoint_calls_domain_methods_and_reports_rejections(tmp_path):
    """Verify POST /{id}/action dispatches to the aggregate's own methods.

    id: TST-WIRE-001
    Given: A generated workspace whose domain class has gained a method (as the TDD loop adds them)
    When: The action endpoint is called with that method's name, bad input, an unknown name and a private name
    Then: The method runs and its state change persists; domain errors are 400; unknown/missing are 404;
          wrong parameters are 422; non-action members are not callable
    """
    structure = DomainStructureSchema(
        domain_name="Demo",
        entities=[EntitySpec(name="Widget", is_aggregate_root=True, attributes=[
            AttributeSpec(name="id", type="str", required=True),
            AttributeSpec(name="label", type="str", required=True),
        ])],
        value_objects=[],
    )
    ws = str(tmp_path)
    build_and_write_skeleton(structure, target_dir=ws)

    domain = os.path.join(ws, "src", "domain", "widget.py")
    with open(domain, "a", encoding="utf-8") as f:
        f.write(textwrap.dedent('''

            def _rename(self, new_label: str) -> str:
                if not new_label:
                    raise ValueError("label must not be empty")
                self.label = new_label
                return f"renamed to {new_label}"

            Widget.rename = _rename
        '''))

    proc = subprocess.run([sys.executable, "-c", CLIENT_SCRIPT], cwd=ws, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[-1500:]
    import json
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    assert out["created"] == 201
    assert out["rename"][0] == 200 and out["rename"][1]["success"] is True
    assert out["rename"][1]["state"]["label"] == "second" and "second" in out["rename"][1]["message"]
    assert out["state_persisted"] == "second"
    assert out["domain_error"][0] == 400 and "empty" in out["domain_error"][1]["detail"]
    assert out["unknown"] == [404]
    assert out["missing_entity"] == 404
    assert out["bad_params"] == 422
    assert out["private"] == 404


SUCCESSOR_SCRIPT = textwrap.dedent('''
    import json, sys
    from fastapi.testclient import TestClient
    from src.app import app

    c = TestClient(app)
    out = {}
    c.post("/api/widgets", json={"id": "w1", "label": "first"})
    answer = c.post("/api/widgets/w1/action", json={"action_type": "copy"}).json()
    out["state"] = answer["state"]
    out["created"] = answer["created"]
    out["stored"] = sorted(w["label"] for w in c.get("/api/widgets").json())
    out["fetched"] = c.get("/api/widgets/" + answer["created"]["id"]).status_code
    plain = c.post("/api/widgets/w1/action", json={"action_type": "rename", "params": {"new_label": "second"}}).json()
    out["plain_created"] = plain["created"]
    print("RESULT=" + json.dumps(out))
''')


def test_a_record_an_action_returns_is_stored_and_answered(tmp_path):
    """An action that makes a new record of its own kind hands it to the caller.

    id: TST-WIRE-002
    Given: A generated workspace whose domain class has one method that returns a new record of the same class
           and one that only changes the record it is called on
    When: Each is run through the action endpoint
    Then: The new record is stored and answered as `created` beside the acted-on record's `state`;
          an action that makes no record answers `created` as null
    """
    structure = DomainStructureSchema(
        domain_name="Demo",
        entities=[EntitySpec(name="Widget", is_aggregate_root=True, attributes=[
            AttributeSpec(name="id", type="str", required=True),
            AttributeSpec(name="label", type="str", required=True),
        ])],
        value_objects=[],
    )
    ws = str(tmp_path)
    build_and_write_skeleton(structure, target_dir=ws)

    with open(os.path.join(ws, "src", "domain", "widget.py"), "a", encoding="utf-8") as f:
        f.write(textwrap.dedent('''

            def _copy(self) -> "Widget":
                self.label = self.label + " (copied)"
                return Widget(id=self.id + "-copy", label="copy of first")

            def _rename(self, new_label: str) -> None:
                self.label = new_label

            Widget.copy = _copy
            Widget.rename = _rename
        '''))

    proc = subprocess.run([sys.executable, "-c", SUCCESSOR_SCRIPT], cwd=ws, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[-1500:]
    import json
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    assert (out["state"]["id"], out["state"]["label"]) == ("w1", "first (copied)")
    assert (out["created"]["id"], out["created"]["label"]) == ("w1-copy", "copy of first")
    assert out["stored"] == ["copy of first", "first (copied)"]
    assert out["fetched"] == 200
    assert out["plain_created"] is None


HANDED_SCRIPT = textwrap.dedent('''
    import json, sys
    from fastapi.testclient import TestClient
    from src.app import app

    c = TestClient(app)
    out = {}
    c.post("/api/dishes", json={"id": "d1", "name": "soup", "left": 1})
    made = c.post("/api/orders/action", json={"action_type": "place_order", "params": {"dish_id": "d1"}})
    out["made"] = [made.status_code, made.json()["created"]["dish_id"], len(made.json()["records"])]
    out["stored"] = [o["dish_id"] for o in c.get("/api/orders").json()]
    out["dish_left"] = c.get("/api/dishes/d1").json()["left"]
    again = c.post("/api/orders/action", json={"action_type": "place_order", "params": {"dish_id": "d1"}})
    out["refused"] = [again.status_code, again.json()["detail"]]
    out["still_one"] = len(c.get("/api/orders").json())
    order_id = made.json()["created"]["id"]
    out["on_record_is_not_on_kind"] = c.post("/api/orders/action", json={"action_type": "cancel"}).status_code
    out["on_kind_is_not_on_record"] = c.post(f"/api/orders/{order_id}/action", json={"action_type": "place_order", "params": {"dish_id": "d1"}}).status_code
    out["bad_params"] = c.post("/api/orders/action", json={"action_type": "place_order", "params": {"wrong": 1}}).status_code
    out["private"] = c.post("/api/orders/action", json={"action_type": "_secret"}).status_code
    gone = c.post(f"/api/orders/{order_id}/action", json={"action_type": "cancel"})
    out["cancel"] = gone.status_code
    out["after_cancel"] = [len(c.get("/api/orders").json()), c.get("/api/dishes/d1").json()["left"]]
    print("RESULT=" + json.dumps(out))
''')


def test_a_method_is_handed_the_stored_records_it_asks_for(tmp_path):
    """Verify a rule that depends on other records is enforced by the app and not only by the class's tests.

    The API ran a method on one record and gave it nothing else, and made a record by constructing the class from
    the request. A product where a person makes records under rules (a table already taken, a dish sold out) had
    no way to apply them: the class that passed its tests held the tests' own records as constants.

    id: TST-WIRE-003
    Given: A generated workspace of two kinds, where one class has a static method that takes both kinds' stored
           records and a method on one record that takes them too
    When: The static method is sent to the kind's action endpoint and the other to a record's
    Then: Each is handed the stored records by their collection names; a record appended is stored and answered as
          `created`, a record removed is gone, a change to a record of the other kind is kept, a refusal is 400 and
          stores nothing, and neither endpoint runs the other's kind of method
    """
    structure = DomainStructureSchema(
        domain_name="Demo",
        entities=[
            EntitySpec(name="Order", is_aggregate_root=True, attributes=[
                AttributeSpec(name="id", type="str", required=True),
                AttributeSpec(name="dish_id", type="str", required=False)]),
            EntitySpec(name="Dish", is_aggregate_root=True, attributes=[
                AttributeSpec(name="id", type="str", required=True),
                AttributeSpec(name="name", type="str", required=True),
                AttributeSpec(name="left", type="int", required=True)]),
        ],
        value_objects=[],
    )
    ws = str(tmp_path)
    build_and_write_skeleton(structure, target_dir=ws)
    with open(os.path.join(ws, "src", "domain", "order.py"), "a", encoding="utf-8") as f:
        f.write(textwrap.dedent('''

            def _place_order(dish_id, orders, dishes):
                import uuid
                dish = next(d for d in dishes if d.id == dish_id)
                if dish.left < 1:
                    raise ValueError("sold out")
                dish.left -= 1
                order = Order(id=uuid.uuid4().hex, dish_id=dish_id)
                orders.append(order)
                return order


            def _cancel(self, orders, dishes):
                next(d for d in dishes if d.id == self.dish_id).left += 1
                orders.remove(self)

            Order.place_order = staticmethod(_place_order)
            Order._secret = staticmethod(lambda: None)
            Order.cancel = _cancel
        '''))

    proc = subprocess.run([sys.executable, "-c", HANDED_SCRIPT], cwd=ws, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[-1500:]
    import json
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    assert out["made"] == [200, "d1", 1] and out["stored"] == ["d1"] and out["dish_left"] == 0
    assert out["refused"] == [400, "sold out"] and out["still_one"] == 1
    assert out["on_record_is_not_on_kind"] == 404 and out["on_kind_is_not_on_record"] == 404
    assert out["bad_params"] == 422 and out["private"] == 404
    assert out["cancel"] == 200 and out["after_cancel"] == [0, 1]
