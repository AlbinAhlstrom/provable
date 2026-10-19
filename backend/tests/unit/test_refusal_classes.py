"""A refusal's class and its sentence are written by code from the contract (vault: Shared Decisions Inventory, row 1).

The contract names each refusal with the exact sentence a person reads. That sentence used to reach the class's
writer as prose ("raised with exactly this message"): one class in a run kept it, another in the same run raised
`rows must be 9..24`, and every page test that waited for the contract's sentence failed. The class is now written
by code, its sentence fixed inside it, and the class's writer only raises it.
"""
import os

import pytest

from onboarding.action_protocol import WRITTEN_FROM_CONTRACT, refusal_classes, shared_words, write_refusals
from onboarding.cst_isolator import FragmentError, merge_module_fragment
from onboarding.router_engine import DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

MANIFEST = {
    "actions": [{"name": "add_guest", "aggregate": "Booking", "params": ["guests"], "description": "adds guests"}],
    "rejections": [
        {"aggregate": "Booking", "error": "TooManyGuestsError", "raised_when": "guests above 8",
         "sentence": "We seat at most 8 at one table."},
        {"aggregate": "Booking", "error": "ClosedDayError", "raised_when": "the day is a closed day",
         "sentence": 'We are closed that day ("Monday").'},
        {"aggregate": "Order", "error": "EmptyOrderError", "raised_when": "no lines", "sentence": "Add a line first."},
    ],
}

STRUCTURE = DomainStructureSchema(domain_name="Tables", entities=[
    EntitySpec(name="Booking", is_aggregate_root=True, attributes=[
        {"name": "id", "type": "string"}, {"name": "guests", "type": "integer"}]),
])


def _module(source):
    scope = {}
    exec(compile(source, "booking.py", "exec"), scope)
    return scope


def test_a_refusal_class_carries_its_sentence_and_takes_no_message():
    """Verify the code written for a class's refusals.

    id: TST-REFUSAL-CLASS
    Given: A manifest with two refusals of Booking, one sentence holding quotes, and one refusal of Order
    When: Booking's refusal classes are written
    Then: Each is raised with no argument and reads as its sentence; handing it a message of its own is a TypeError;
          Order's refusal is not among them; the names are listed as written from the contract
    """
    scope = _module(refusal_classes(MANIFEST, "Booking"))

    assert str(scope["TooManyGuestsError"]()) == "We seat at most 8 at one table."
    assert str(scope["ClosedDayError"]()) == 'We are closed that day ("Monday").'
    with pytest.raises(TypeError):
        scope["TooManyGuestsError"]("guests must be 1..8")
    assert "EmptyOrderError" not in scope
    assert scope[WRITTEN_FROM_CONTRACT] == ("TooManyGuestsError", "ClosedDayError")


def test_the_refusals_are_written_into_the_class_module_once(tmp_path):
    """Verify the refusals are put beside the class in its module, and writing them again changes nothing.

    id: TST-REFUSAL-WRITE
    Given: A skeleton with Booking's module, and the manifest
    When: The refusals are written twice
    Then: Booking's module defines each refusal once, before the class, and still imports and defines Booking
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    write_refusals(MANIFEST, str(tmp_path))
    write_refusals(MANIFEST, str(tmp_path))

    path = os.path.join(tmp_path, "src", "domain", "booking.py")
    source = open(path, encoding="utf-8").read()
    assert source.count("class TooManyGuestsError") == 1 and source.count(f"{WRITTEN_FROM_CONTRACT} =") == 1
    assert source.index("class TooManyGuestsError") < source.index("class Booking")
    scope = _module(source)
    assert str(scope["ClosedDayError"]()) == 'We are closed that day ("Monday").' and "Booking" in scope


def test_a_code_answer_does_not_replace_a_refusal_written_from_the_contract(tmp_path):
    """Verify the class's writer cannot rewrite a refusal's sentence.

    id: TST-REFUSAL-MERGE
    Given: Booking's module with its refusals written, and a code answer that defines TooManyGuestsError again with
           a message of its own beside the class's method
    When: The answer is merged
    Then: The refusal keeps the contract's sentence and the class gets its method
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    write_refusals(MANIFEST, str(tmp_path))
    path = os.path.join(tmp_path, "src", "domain", "booking.py")
    answer = (
        "class TooManyGuestsError(Exception):\n"
        "    def __init__(self, message='guests must be 1..8'):\n"
        "        super().__init__(message)\n\n\n"
        "class Booking:\n"
        "    def add_guest(self, guests):\n"
        "        if guests > 8:\n"
        "            raise TooManyGuestsError()\n"
        "        self.guests = guests\n")

    merged = merge_module_fragment(open(path, encoding="utf-8").read(), "Booking", answer)

    scope = _module(merged)
    assert str(scope["TooManyGuestsError"]()) == "We seat at most 8 at one table."
    with pytest.raises(Exception) as refused:
        scope["Booking"](id="b1", guests=2).add_guest(9)
    assert str(refused.value) == "We seat at most 8 at one table."


def test_the_writers_are_told_to_raise_a_refusal_with_no_message():
    """Verify the words every writer of the class shares say how a refusal is raised.

    id: TST-REFUSAL-WORDS
    Given: The manifest
    When: Booking's shared words are rendered
    Then: Each refusal is to be raised with no arguments, and its sentence is not left to the writer
    """
    lines = "\n".join(shared_words(MANIFEST, "Booking"))
    assert "`TooManyGuestsError()`" in lines and "no arguments" in lines


def test_a_module_whose_list_of_written_helpers_cannot_be_read_refuses_the_answer(tmp_path):
    """
    id: TST-REFUSAL-UNREAD
    Given: Booking's module whose list of helpers written from the contract is not a literal
    When: A code answer is merged into it
    Then: The merge fails by naming the list, instead of letting the answer replace the helpers
    """
    source = f"{WRITTEN_FROM_CONTRACT} = tuple(NAMES)\n\n\nclass Booking:\n    pass\n"
    with pytest.raises(FragmentError, match=WRITTEN_FROM_CONTRACT):
        merge_module_fragment(source, "Booking", "class Booking:\n    def go(self):\n        return 1\n")
