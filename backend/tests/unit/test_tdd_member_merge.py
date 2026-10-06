"""GREEN merges member-by-member: unmentioned fields/methods survive, so the model need not rewrite the whole class."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.cst_isolator import merge_module_fragment

MODULE = '''from dataclasses import dataclass
from typing import Optional


@dataclass
class Booking:
    """A booking."""

    id: str
    status: str = "NEW"

    def confirm(self) -> None:
        self.status = "CONFIRMED"

    def cancel(self) -> None:
        self.status = "CANCELLED"
'''


def _run(fragment):
    out = merge_module_fragment(MODULE, "Booking", fragment)
    compile(out, "m", "exec")
    return out


def test_unmentioned_members_are_kept():
    """Verify a fragment adding one method leaves every other member untouched.

    id: TST-MRG-001
    Given: A class with confirm and cancel and a fragment that only adds reschedule
    When: The fragment is merged
    Then: confirm, cancel and the fields are all still there, plus reschedule
    """
    out = _run("@dataclass\nclass Booking:\n    def reschedule(self, new_start: str) -> None:\n        self.status = 'MOVED'\n")
    for name in ("def confirm", "def cancel", "def reschedule", "id: str", 'status: str = "NEW"'):
        assert name in out
    assert out.count("class Booking") == 1 and '"""A booking."""' in out


def test_a_mentioned_method_is_replaced_not_duplicated():
    """Verify changing a method replaces it in place.

    id: TST-MRG-002
    Given: A fragment redefining cancel
    When: It is merged
    Then: cancel exists once with the new body, and confirm is unchanged
    """
    out = _run("@dataclass\nclass Booking:\n    def cancel(self, fee: float = 0.0) -> None:\n        self.status = 'CANCELLED_WITH_FEE'\n")
    assert out.count("def cancel") == 1 and "CANCELLED_WITH_FEE" in out and 'self.status = "CONFIRMED"' in out


def test_new_fields_keep_dataclass_ordering_valid():
    """Verify a new field without a default is placed before fields with defaults.

    id: TST-MRG-003
    Given: A fragment adding a required field and a defaulted field
    When: It is merged and the module is executed
    Then: The dataclass can be defined (no 'non-default argument follows default argument' error)
    """
    out = _run("@dataclass\nclass Booking:\n    client_id: str\n    total: float = 0.0\n")
    namespace = {}
    exec(out, namespace)  # raises TypeError if the ordering is invalid
    fields = list(namespace["Booking"].__dataclass_fields__)
    assert fields.index("client_id") < fields.index("status") and "total" in fields


def test_pass_placeholder_is_dropped_when_members_are_added():
    """Verify a placeholder body does not linger beside real members.

    id: TST-MRG-004
    Given: A class whose body is just pass
    When: A fragment adds a method
    Then: The class has the method and no stray pass statement
    """
    out = merge_module_fragment("class Booking:\n    pass\n", "Booking", "class Booking:\n    def go(self) -> int:\n        return 1\n")
    assert "def go" in out and "pass" not in out


def test_missing_target_class_is_inserted_whole():
    """Verify a fragment for a class the module does not have yet still works.

    id: TST-MRG-005
    Given: A module without the target class
    When: A fragment defines it
    Then: The class is appended
    """
    out = merge_module_fragment("X = 1\n", "Booking", "@dataclass\nclass Booking:\n    id: str = ''\n")
    assert "class Booking" in out and "X = 1" in out


def test_green_prompt_asks_only_for_added_or_changed_members():
    """Verify the model is told it need not rewrite the whole class.

    id: TST-MRG-006
    Given: The green_class_repair prompt
    When: Its text is read
    Then: It says to return only added/changed members and that omitted members are kept
    """
    text = open(os.path.join(os.path.dirname(merge_module_fragment.__code__.co_filename), "..", "prompts", "green_class_repair.md"), encoding="utf-8").read().lower()
    assert "only the fields and methods you add or change" in text and "kept exactly as they are" in text
