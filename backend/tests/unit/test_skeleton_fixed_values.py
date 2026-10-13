"""A record is created only with values its fields can take: the generated API refuses any other, by name."""

import json
import os
import subprocess
import sys
import textwrap

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding.router_engine import AttributeSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

CLIENT_SCRIPT = textwrap.dedent('''
    import json
    from fastapi.testclient import TestClient
    from src.app import app

    c = TestClient(app)
    out = {}
    for name, body in {
        "inside": {"id": "o1", "status": "sent", "lines": [{"dish": "soup", "state": "served"}]},
        "defaults": {"id": "o2"},
        "outside": {"id": "o3", "status": "send"},
        "part_outside": {"id": "o4", "lines": [{"dish": "soup", "state": "served"}, {"dish": "pie", "state": "serve"}]},
        "free_text": {"id": "o5", "note": "anything at all"},
    }.items():
        answer = c.post("/api/orders", json=body)
        out[name] = [answer.status_code, answer.json().get("detail")]
    out["stored"] = sorted(o["id"] for o in c.get("/api/orders").json())
    print("RESULT=" + json.dumps(out))
''')


def test_a_creation_with_a_value_outside_a_fixed_set_is_refused(tmp_path):
    """Verify a record cannot start in a state the product does not have, so whoever arranges one hears of a
    misspelt value at once instead of working on with a record no rule covers.

    id: TST-SKELETON-FIXED-VALUES
    Given: A generated app whose class has a field with a fixed set of values, a list of parts whose items have
           one, and a field of free text
    When: Records are created with values inside the sets, with none, with a value outside the field's set, with
          a value outside the set of a part's field, and with any text in the free field
    Then: The first two and the last are stored; the two with a value outside a set are refused with 422 and a
          sentence naming the field, the values it takes and the value sent, and are not stored
    """
    structure = DomainStructureSchema(
        domain_name="Demo",
        entities=[EntitySpec(name="Order", is_aggregate_root=True, attributes=[
            AttributeSpec(name="id", type="str", required=True),
            AttributeSpec(name="status", type="str", required=False, default_value="draft", values=["draft", "sent"]),
            AttributeSpec(name="note", type="str", required=False),
            AttributeSpec(name="lines", type="list", required=False, item_name="Line", item_attributes=[
                AttributeSpec(name="dish", type="str"),
                AttributeSpec(name="state", type="str", values=["waiting", "served"])]),
        ])],
        value_objects=[],
    )
    ws = str(tmp_path)
    build_and_write_skeleton(structure, target_dir=ws)

    proc = subprocess.run([sys.executable, "-c", CLIENT_SCRIPT], cwd=ws, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[-1500:]
    out = json.loads(next(l for l in proc.stdout.splitlines() if l.startswith("RESULT="))[len("RESULT="):])

    assert out["inside"][0] == 201 and out["defaults"][0] == 201 and out["free_text"][0] == 201
    assert out["outside"] == [422, 'Order.status is one of "draft", "sent"; "send" is none of them.']
    assert out["part_outside"] == [422, 'Order.lines: state of item 2 is one of "waiting", "served"; "serve" is none of them.']
    assert out["stored"] == ["o1", "o2", "o5"]
