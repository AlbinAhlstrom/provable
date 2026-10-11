"""The page is written while its actions are implemented, and checked against the classes afterwards
(backend/onboarding/page_contract.py).

The page reads the records the API serves: the fields of the domain classes. It used to wait for the actions'
methods, a minute or more, although what it is shown of them (their names, the values the fields take, what a new
object holds) is fixed by the action protocol before any method exists. It is now written at once, from the classes
as the skeleton left them. Writing the methods can still change what a class holds, so the fields are compared
afterwards, and only a class that changed sends the page back to be written again.
"""
from onboarding.page_contract import FieldChange, domain_fields, field_changes

ORDER = '''from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Order:
    """lines: the Line records this Order owns."""
    id: str
    status: str = "open"
    lines: List[Dict[str, Any]] = field(default_factory=list)
    events: List[Any] = field(default_factory=list)
    _reserved: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        total: int = 0
        return {"id": self.id, "total": total}
'''


def _domain(tmp_path, **modules):
    folder = tmp_path / "src" / "domain"
    folder.mkdir(parents=True, exist_ok=True)
    for name, source in modules.items():
        (folder / f"{name}.py").write_text(source, encoding="utf-8")
    return str(tmp_path)


def test_the_fields_a_class_serves_are_read_from_its_source(tmp_path):
    """Verify what the page can read of a class is its public fields, and nothing else of the module.

    id: TST-PAGE-CONTRACT-001
    Given: A domain module with a dataclass that has public fields, a private field and a method with a local variable,
           beside the shared events and exceptions modules
    When: The domain's fields are read
    Then: The class is listed with its public fields in order; the private field, the method's local and the shared
          modules are left out
    """
    workspace = _domain(tmp_path, order=ORDER, events="class DomainEvent:\n    name: str = ''\n",
                        exceptions="class DomainError(Exception):\n    code: int = 0\n")
    assert domain_fields(workspace) == {"Order": ["id", "status", "lines", "events"]}


def test_a_workspace_without_a_domain_has_no_fields(tmp_path):
    """Verify reading the fields of a workspace that has no domain yet is an empty answer, not an error.

    id: TST-PAGE-CONTRACT-002
    Given: A workspace with no src/domain folder
    When: The domain's fields are read
    Then: Nothing is listed
    """
    assert domain_fields(str(tmp_path)) == {}


def test_classes_that_hold_what_they_held_need_no_second_look():
    """Verify the usual case costs nothing: the methods were written and the fields are the same.

    id: TST-PAGE-CONTRACT-003
    Given: The fields before and after the actions were implemented, identical but for their order
    When: They are compared
    Then: No change is reported
    """
    before = {"Order": ["id", "status", "lines"], "Customer": ["id", "name"]}
    assert field_changes(before, {"Customer": ["id", "name"], "Order": ["id", "lines", "status"]}) == []


def test_a_class_that_gained_or_lost_a_field_is_named_with_the_fields():
    """Verify a change to what a class holds is reported by class and field, in words a page writer can act on.

    id: TST-PAGE-CONTRACT-004
    Given: One class that gained two fields and lost one while its actions were written, and one that did not change
    When: The fields are compared
    Then: Only the changed class is reported, with what it gained and lost, and its description names them
    """
    before = {"Match": ["id", "status", "turn"], "Player": ["id", "name"]}
    after = {"Match": ["id", "status", "winner", "pieces"], "Player": ["id", "name"]}
    changes = field_changes(before, after)
    assert changes == [FieldChange(class_name="Match", added=["winner", "pieces"], removed=["turn"])]
    assert changes[0].describe() == "Match now also holds winner, pieces and no longer holds turn"


def test_a_class_written_during_the_actions_is_a_change_too():
    """Verify a class that did not exist when the page was written is reported with everything it holds.

    id: TST-PAGE-CONTRACT-005
    Given: A class that only exists after the actions were implemented
    When: The fields are compared
    Then: It is reported as having gained all of its fields
    """
    changes = field_changes({"Order": ["id"]}, {"Order": ["id"], "Line": ["id", "quantity"]})
    assert changes == [FieldChange(class_name="Line", added=["id", "quantity"], removed=[])]
    assert changes[0].describe() == "Line now also holds id, quantity"
