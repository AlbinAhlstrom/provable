"""The first tests of a class's rules are written in one answer (onboarding/first_tests.py).

The product contract states each rule as a situation with its values, one action and the values afterwards. Turning
that into a test is transcription, so one writer does it for every rule of a class at once, without thinking, and
each rule's test is then cut out of the answer and judged by the gates on its own.
"""
import ast

from onboarding import first_tests
from onboarding.router_engine import BusinessSpec

MODULE = '''import pytest
from src.domain.order import Order

LIMIT = 3


def build_two_lines_unsent():
    order = Order(id="1")
    order.lines = [{"item": "soup"}, {"item": "bread"}]
    return order


def test_spec_001_a_line_is_added():
    order = build_two_lines_unsent()
    order.add_line(item="tea")
    assert len(order.lines) == LIMIT


@pytest.mark.parametrize("count", [3, 4])
def test_spec_002_at_the_limit(count):
    assert count >= LIMIT


def test_spec_002_beyond_the_limit():
    order = build_two_lines_unsent()
    assert order.lines


def test_spec_0021_is_another_rule():
    assert build_two_lines_unsent()


def test_something_no_rule_asked_for():
    assert True
'''


def _spec(spec_id, **fields):
    return BusinessSpec(**{"spec_id": spec_id, "title": f"Rule {spec_id}", "description": "d",
                           "given_when_then": "Given two_lines_unsent, When add_line(item 'tea'), Then three lines",
                           "target_aggregate": "Order", **fields})


def test_each_rule_gets_its_own_tests_and_everything_they_share():
    """
    id: TST-FIRST-001
    Given: One module with a builder, a constant, and test functions named after the rules' ids
    When: It is cut up by rule
    Then: Each rule's module holds the imports, the constant and the builder, and only its own test functions
          (with their decorators); a test no rule asked for is in none
    """
    cut = first_tests.split_by_rule(MODULE, ["SPEC-001", "SPEC-002", "SPEC-0021"])

    for source in cut.values():
        ast.parse(source)
        assert "from src.domain.order import Order" in source and "LIMIT = 3" in source
        assert "def build_two_lines_unsent" in source and "no_rule_asked_for" not in source
    assert "test_spec_001_a_line_is_added" in cut["SPEC-001"] and "test_spec_002" not in cut["SPEC-001"]
    assert "test_spec_002_at_the_limit" in cut["SPEC-002"] and "test_spec_002_beyond_the_limit" in cut["SPEC-002"]
    assert '@pytest.mark.parametrize("count", [3, 4])' in cut["SPEC-002"]
    assert "test_spec_0021" not in cut["SPEC-002"] and "test_spec_0021_is_another_rule" in cut["SPEC-0021"]


def test_a_rule_the_answer_left_out_has_no_test():
    """
    id: TST-FIRST-002
    Given: An answer with no test function for one of the rules, and an answer that is not Python
    When: Each is cut up by rule
    Then: The rule left out gets an empty test (which the gate refuses, and its writer is asked again); the answer
          that is not Python is given to every rule whole, so the refusal names what is wrong with it
    """
    assert first_tests.split_by_rule(MODULE, ["SPEC-001", "SPEC-009"])["SPEC-009"] == ""
    assert first_tests.split_by_rule("def broken(:\n", ["SPEC-001", "SPEC-002"]) == {
        "SPEC-001": "def broken(:\n", "SPEC-002": "def broken(:\n"}


def test_one_writer_is_given_every_rule_of_the_class_and_each_situation_once(monkeypatch):
    """
    id: TST-FIRST-003
    Given: Three rules of one class, two of them starting from the same situation and one stating a limit
    When: Their first tests are written
    Then: One call is made, on the stage that answers without thinking; its prompt names each rule's test function,
          holds each rule's line, the shared situation once, and says which rule states a limit; the answer comes
          back cut up by rule
    """
    import agent_orchestrator
    asked = []

    def answer(prompt, stage="general", **kwargs):
        asked.append((prompt, stage))
        return "Here it is:\n```python\n" + MODULE + "```"
    monkeypatch.setattr(agent_orchestrator, "call_gemini", answer)
    situation = "`two_lines_unsent`: an order of two lines, not sent: lines soup, bread; status draft"
    specs = [_spec("SPEC-001", situation=situation), _spec("SPEC-002", situation=situation, is_mathematical_boundary=True),
             _spec("SPEC-NEW-ORDER", given_when_then="Given nothing, When an Order is created, Then status draft")]

    cut = first_tests.write_first_tests(specs, "class Order:\n    id: str\n", "order", "Order",
                                        interface_contract="- `add_line(item)`")

    (prompt, stage), = asked
    assert stage == first_tests.STAGE == "first_tests"
    assert prompt.count(situation) == 1 and "from src.domain.order import Order" in prompt and "- `add_line(item)`" in prompt
    assert "`test_spec_001`" in prompt and "`test_spec_new_order`" in prompt
    assert "Given two_lines_unsent, When add_line(item 'tea'), Then three lines" in prompt
    limit_lines = [line for line in prompt.splitlines() if "states a limit" in line and "`test_spec_" in line]
    assert len(limit_lines) == 1 and "`test_spec_002`" in limit_lines[0]
    assert "test_spec_001_a_line_is_added" in cut["SPEC-001"] and cut["SPEC-NEW-ORDER"] == ""


def test_an_empty_answer_fails_with_the_providers_reason(monkeypatch):
    """
    id: TST-FIRST-004
    Given: A provider that returns nothing
    When: The first tests are written
    Then: It fails with the provider's reason, and nothing is tried again
    """
    import agent_orchestrator
    import pytest
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda *a, **k: calls.append(1) or "")
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "quota exceeded", raising=False)

    with pytest.raises(RuntimeError, match="quota exceeded"):
        first_tests.write_first_tests([_spec("SPEC-001")], "class Order:\n    id: str\n", "order", "Order")
    assert len(calls) == 1


def test_the_writers_that_transcribe_answer_without_thinking():
    """
    id: TST-FIRST-005
    Given: The provider whose small model thinks by default
    When: The first tests' stage is connected
    Then: It runs on the small model with thinking off, as the page writer does
    """
    import llm_provider
    provider = llm_provider.PROVIDERS["anthropic"]

    assert first_tests.STAGE in provider.unthinking_stages and first_tests.STAGE not in provider.stage_models
