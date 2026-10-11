"""The action protocol is designed before the specs run; it must be checked against the methods that exist afterwards."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding.action_protocol import check_action_contract
from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork

MANIFEST = {"actions": [
    {"name": "submit_inquiry", "aggregate": "CareInquiry", "performed_by": "audience"},
    {"name": "Acknowledge Inquiry", "aggregate": "CareInquiry", "performed_by": "other"},
    {"name": "cancel", "aggregate": "CareInquiry"},
]}
DOMAIN = '''class CareInquiry:
    def submit_inquiry(self, email):
        pass

    def acknowledge_inquiry(self):
        pass

    def _private(self):
        pass
'''


def _workspace(tmp_path, code=DOMAIN):
    d = tmp_path / "src" / "domain"
    d.mkdir(parents=True)
    (d / "care_inquiry.py").write_text(code, encoding="utf-8")
    return str(tmp_path)


def test_manifest_actions_without_a_method_are_reported(tmp_path):
    """Verify an action the interface may call but the domain lacks is reported with its aggregate and audience.

    id: TST-ACT-001
    Given: A manifest of three actions and a class implementing two (one under a differently cased name)
    When: The contract is checked
    Then: Only the third is missing; the router's name normalisation is applied; private methods do not count
    """
    result = check_action_contract(_workspace(tmp_path), MANIFEST)
    assert result["ok"] is False
    assert result["missing"] == [{"action": "cancel", "aggregate": "CareInquiry", "performed_by": "audience"}]
    assert set(result["implemented"]) == {"submit_inquiry", "Acknowledge Inquiry"}


def test_missing_domain_module_means_every_action_is_missing(tmp_path):
    """Verify a manifest against a workspace without the aggregate reports everything missing, not a crash.

    id: TST-ACT-002
    Given: An empty workspace
    When: The contract is checked
    Then: All actions are missing
    """
    assert len(check_action_contract(str(tmp_path), MANIFEST)["missing"]) == 3
    assert check_action_contract(str(tmp_path), None) == {"ok": True, "implemented": [], "missing": []}


def test_service_checks_the_persisted_manifest(tmp_path):
    """Verify the service reads the manifest stored at kickstart and checks it against the workspace.

    id: TST-ACT-003
    Given: A stored manifest and a workspace implementing part of it
    When: get_action_contract is called
    Then: The missing action is reported
    """
    uow = FakeUnitOfWork()
    with uow:
        state = uow.kickstart.get()
        state.action_manifest = MANIFEST
        uow.kickstart.save(state)
        uow.commit()
    result = services.get_action_contract(uow, workspace_dir=_workspace(tmp_path))
    assert [m["action"] for m in result["missing"]] == ["cancel"]


def test_manifest_survives_the_sqlite_round_trip():
    """Verify the manifest is persisted with the kickstart state, including on a database created before the column existed.

    id: TST-ACT-004
    Given: A manifest saved through the real store (hermetic test database)
    When: The kickstart state is read back
    Then: The manifest is intact
    """
    from db import store
    state = store.get_kickstart_state()
    state["action_manifest"] = MANIFEST
    store.save_kickstart_state(state)
    assert store.get_kickstart_state()["action_manifest"] == MANIFEST


def test_red_prompt_promises_the_manifest_methods_of_the_target_class(monkeypatch):
    """Verify the test writer is told which method names the interface will call, per aggregate.

    id: TST-ACT-005
    Given: A manifest with actions on two aggregates and a spec for one of them
    When: The RED test is generated
    Then: The prompt lists that aggregate's action names and parameters and not the other aggregate's
    """
    import agent_orchestrator
    from onboarding.router_engine import BusinessSpec
    from service_layer import tdd_machine as tm
    manifest = {"actions": [
        {"name": "submit_inquiry", "aggregate": "CareInquiry", "params": ["email"], "description": "Send"},
        {"name": "calculate_estimate", "aggregate": "ServiceOffering", "params": ["hours"]}]}
    seen = {}
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: seen.setdefault("p", p) and "```python\nx\n```")
    spec = BusinessSpec(spec_id="S", title="T", description="d", given_when_then="g", target_aggregate="CareInquiry")
    tm.generate_red_test(spec, "class CareInquiry:\n    pass\n", "care_inquiry", "CareInquiry",
                         interface_contract=tm.format_interface_contract(manifest, "CareInquiry"))
    assert "submit_inquiry" in seen["p"] and "email" in seen["p"] and "calculate_estimate" not in seen["p"]
    assert "none: no interface method" in tm.format_interface_contract(manifest, "Other")


def test_the_interface_says_which_stored_records_a_method_is_handed():
    """Verify the writers of a class's tests and code are told the same way to reach other records.

    id: TST-ACT-006
    Given: A manifest with an action sent to no one record that works with its own kind and another, and an action
           on one record that works with another kind
    When: The interface of the class is written out
    Then: The first is a static method handed both lists by their collection names, the second an ordinary method
          handed the one list, and the other kind is shown with the fields it is built from
    """
    from onboarding.action_protocol import format_interface_contract
    manifest = {"actions": [
        {"name": "place_order", "aggregate": "Order", "params": ["dish_id"], "given": ["Order", "Dish"], "on_kind": True},
        {"name": "cancel_order", "aggregate": "Order", "params": [], "given": ["Dish"], "on_kind": False},
        {"name": "send_order", "aggregate": "Order", "params": []}],
        "records": [{"aggregate": "Order", "fields": ["id", "status"]}, {"aggregate": "Dish", "fields": ["id", "price"]}]}

    text = format_interface_contract(manifest, "Order")
    place, cancel, send = (next(l for l in text.splitlines() if f"`{n}`" in l)
                           for n in ("place_order", "cancel_order", "send_order"))

    assert "`@staticmethod`" in place and "`Order.place_order(...)`" in place
    assert "`orders`" in place and "`dishes`" in place and "uuid.uuid4().hex" in place
    assert "`@staticmethod`" not in cancel and "`dishes`" in cancel and "`orders`" not in cancel
    assert "removes from its list" in cancel
    assert "by keyword" not in send
    # every line says how its method is called: a writer shown one static method wrote the others static too
    assert "called on that record as `order.send_order(...)`" in send and "`order.cancel_order(...)`" in cancel
    assert "called on that record" not in place
    assert "`Dish(id=..., price=...)`" in text and "from src.domain.dish import Dish" in text
