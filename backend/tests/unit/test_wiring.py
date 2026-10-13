"""An app that exists gets the generator's current routers and API clients without being built again."""
import os

from onboarding.router_engine import AttributeSpec, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton, generate_master_client, generate_router_module
from onboarding.wiring import refresh_wiring
from service_layer import app_wiring
from service_layer.unit_of_work import FakeUnitOfWork

WIDGET = EntitySpec(name="Widget", is_aggregate_root=True, attributes=[
    AttributeSpec(name="id", type="str", required=True), AttributeSpec(name="label", type="str", required=True)])
STRUCTURE = DomainStructureSchema(domain_name="Demo", entities=[WIDGET], value_objects=[])
ROUTER = os.path.join("src", "entrypoints", "routers", "widget.py")
CLIENT = os.path.join("src", "api", "widgetClient.ts")
DOMAIN = os.path.join("src", "domain", "widget.py")


def _read(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as f:
        return f.read()


def _write(root, rel, text):
    os.makedirs(os.path.dirname(os.path.join(root, rel)), exist_ok=True)
    with open(os.path.join(root, rel), "w", encoding="utf-8") as f:
        f.write(text)


def test_a_router_and_a_client_from_an_older_generator_are_written_again(tmp_path):
    """
    Given: An app whose router and API client were written by an older generator, and a domain class that has
           gained a method since
    When: The app's wiring is refreshed
    Then: The router and the client are what the generator writes today, the two are named as rewritten,
          and the domain class is as it was
    """
    root = str(tmp_path)
    build_and_write_skeleton(STRUCTURE, target_dir=root)
    _write(root, ROUTER, "# an older router\n")
    _write(root, CLIENT, "// an older client\n")
    _write(root, DOMAIN, _read(root, DOMAIN) + "\n# a method written since\n")

    rewritten = refresh_wiring(STRUCTURE, root)

    assert sorted(rewritten) == sorted([ROUTER.replace(os.sep, "/"), CLIENT.replace(os.sep, "/")])
    assert _read(root, ROUTER) == generate_router_module(WIDGET)
    assert _read(root, CLIENT) == generate_master_client(WIDGET)
    assert _read(root, DOMAIN).endswith("# a method written since\n")


def test_wiring_that_is_current_is_left_alone_and_no_file_is_added(tmp_path):
    """
    Given: An app whose router is current and which has no client for its class (the page does not present it)
    When: The app's wiring is refreshed
    Then: Nothing is rewritten and no client appears
    """
    root = str(tmp_path)
    build_and_write_skeleton(STRUCTURE, target_dir=root)
    if os.path.exists(os.path.join(root, CLIENT)):
        os.remove(os.path.join(root, CLIENT))

    assert refresh_wiring(STRUCTURE, root) == []
    assert not os.path.exists(os.path.join(root, CLIENT))


def test_the_current_apps_wiring_is_refreshed_from_its_kept_decomposition(tmp_path):
    """
    Given: A kickstart state that kept its decomposition, and an app with an older router
    When: The use case is run
    Then: It answers with the files it rewrote
    """
    root = str(tmp_path)
    build_and_write_skeleton(STRUCTURE, target_dir=root)
    _write(root, ROUTER, "# an older router\n")
    uow = FakeUnitOfWork()
    with uow:
        state = uow.kickstart.get()
        state.structure = STRUCTURE.model_dump()
        uow.kickstart.save(state)
        uow.commit()

    result = app_wiring.refresh_app_wiring(uow=uow, workspace_dir=root)
    assert result == {"success": True, "rewritten": [ROUTER.replace(os.sep, "/")]}


def test_an_app_without_a_kept_decomposition_says_so(tmp_path):
    """
    Given: A kickstart state with no decomposition
    When: The use case is run
    Then: It fails with the reason and writes nothing
    """
    result = app_wiring.refresh_app_wiring(uow=FakeUnitOfWork(), workspace_dir=str(tmp_path))
    assert result["success"] is False and "decomposition" in result["error"]


def test_a_refreshed_client_keeps_the_action_functions_the_page_calls(tmp_path):
    """
    id: TST-WIRING-ACTIONS
    Given: A kickstart state that kept its decomposition and its actions, and an app with an older client
    When: The use case is run
    Then: The client is the one the generator writes for the class with those actions
    """
    root = str(tmp_path)
    build_and_write_skeleton(STRUCTURE, target_dir=root)
    _write(root, CLIENT, "// an older client\n")
    actions = [{"name": "polish", "aggregate": "Widget", "params": []}]
    uow = FakeUnitOfWork()
    with uow:
        state = uow.kickstart.get()
        state.structure, state.action_manifest = STRUCTURE.model_dump(), {"actions": actions}
        uow.kickstart.save(state)
        uow.commit()

    result = app_wiring.refresh_app_wiring(uow=uow, workspace_dir=root)

    assert result == {"success": True, "rewritten": [CLIENT.replace(os.sep, "/")]}
    assert _read(root, CLIENT) == generate_master_client(WIDGET, actions=actions)
    assert "polish: (id: string)" in _read(root, CLIENT)
