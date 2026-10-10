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
