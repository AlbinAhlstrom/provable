"""A rule whose test the TDD loop corrected is corrected too, so every later reader of the rule meets one outcome.

The contract works out each rule's outcome by hand. When it gets one wrong, the class (written from all the rules)
is right and the rule's first test fails it; the test's writer, shown the failure, corrects the test
(`tdd_batch.reconsider_test`). The page test is written later from the rule's text, so that text is corrected with
the test, or the page test asserts the outcome the unit test was corrected away from.
"""
import agent_orchestrator
from onboarding.router_engine import BusinessSpec
from service_layer import services, tdd_machine
from service_layer.unit_of_work import FakeUnitOfWork

GWT = "Given small_playing, When open_square with row 3, column 3, Then row 3 column 3 open; status playing"
CORRECTED = "row 3 column 3 open; every safe square open; status won"
CODE = "def test_x():\n    assert True\n"


def _deck() -> FakeUnitOfWork:
    uow = FakeUnitOfWork()
    services.add_inbox_spec({"spec_id": "SPEC-002", "title": "Cascade", "given_when_then": GWT}, uow=uow)
    services.add_rule_card({"id": "SPEC-002", "title": "Cascade", "given_clause": "small_playing",
                            "when_clause": "open_square with row 3, column 3",
                            "then_clause": "row 3 column 3 open; status playing"}, uow=uow)
    return uow


def test_a_corrected_test_corrects_the_outcome_its_rule_states():
    """
    id: TST-RULE-CORRECT-001
    Given: A rule in the inbox and on the deck, and a TDD result whose test was corrected with a new outcome
    When: The result is recorded
    Then: The rule's Then is the corrected outcome in its text and on its card; its Given and When are unchanged; the
          outcome it stated before is kept with the result
    """
    uow = _deck()
    services.record_tdd_result("SPEC-002", {"success": True, "status": "FULFILLED", "phase": "COMMITTED",
                                            "reconsidered": True, "corrected_then": CORRECTED}, uow=uow)

    spec = services.get_inbox_specs(uow=uow)[0]
    assert spec["given_when_then"] == ("Given small_playing, When open_square with row 3, column 3, Then " + CORRECTED)
    assert services.get_living_deck(uow=uow)[0]["then_clause"] == CORRECTED
    assert spec["tdd"]["corrected_from"] == "row 3 column 3 open; status playing"


def test_a_result_without_a_corrected_outcome_leaves_the_rule_as_written():
    """
    id: TST-RULE-CORRECT-002
    Given: A rule, and a TDD result that corrected nothing
    When: The result is recorded
    Then: The rule's text and card are as they were
    """
    uow = _deck()
    services.record_tdd_result("SPEC-002", {"success": True, "status": "FULFILLED", "phase": "COMMITTED"}, uow=uow)

    assert services.get_inbox_specs(uow=uow)[0]["given_when_then"] == GWT
    assert services.get_living_deck(uow=uow)[0]["then_clause"] == "row 3 column 3 open; status playing"


def test_the_reconsidering_writer_states_the_outcome_beside_its_corrected_test(monkeypatch):
    """
    id: TST-RULE-CORRECT-003
    Given: A writer asked to reconsider its test, answering with the corrected test and a `Then:` line, and one
           answering with the test alone
    When: The answers are read
    Then: The first gives the code and the outcome; the second gives the code and no outcome; the writer was asked
          for that line
    """
    spec = BusinessSpec(spec_id="SPEC-002", title="Cascade", description="", given_when_then=GWT,
                        target_aggregate="Game", spec_type="DOMAIN_INVARIANT")
    asked = []
    answers = iter([f"The test was wrong.\n\n```python\n{CODE}```\n\nThen: {CORRECTED}\n", f"```python\n{CODE}```\n"])
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, **kw: asked.append(prompt) or next(answers))

    assert tdd_machine.reconsider_red_test(spec, "class Game: ...", "game", "Game", "feedback") == (CODE, CORRECTED)
    assert tdd_machine.reconsider_red_test(spec, "class Game: ...", "game", "Game", "feedback") == (CODE, "")
    assert "Then:" in asked[0]
