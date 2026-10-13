"""One review of the whole spec set reports contradictions up front; it never rewrites specs or retries."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.router_engine import BusinessSpec
from onboarding.spec_review import review_spec_consistency


def _spec(i, gwt):
    return BusinessSpec(spec_id=f"S{i}", title=f"T{i}", description="d", given_when_then=gwt, target_aggregate="Enquiry")


SPECS = [_spec(1, "Given no email When submitted Then it is accepted"), _spec(2, "Given no email When submitted Then it is rejected")]


def _llm(monkeypatch, reply):
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: calls.append((stage, p)) or reply)
    return calls


def test_contradictions_are_reported_with_their_spec_ids(monkeypatch):
    """Verify a contradicting pair is reported and the model sees every spec.

    id: TST-REV-010
    Given: Two specs with opposite outcomes and a model that names them
    When: The set is reviewed
    Then: The conflict lists both ids and the reason; the prompt contained both specs
    """
    calls = _llm(monkeypatch, '{"conflicts": [{"specs": ["S1", "S2", "S-unknown"], "reason": "accepted vs rejected"}]}')
    result = review_spec_consistency(SPECS)
    assert result == {"success": True, "conflicts": [{"specs": ["S1", "S2"], "reason": "accepted vs rejected"}]}
    assert len(calls) == 1 and "S1" in calls[0][1] and "S2" in calls[0][1]


def test_single_spec_needs_no_review_and_failures_are_not_retried(monkeypatch):
    """Verify trivial sets skip the call and provider/parse failures are reported after one call.

    id: TST-REV-011
    Given: One spec; then an empty answer; then invalid JSON
    When: Each is reviewed
    Then: No call for one spec; one call each for the failures, each reported as success False
    """
    calls = _llm(monkeypatch, "")
    assert review_spec_consistency(SPECS[:1]) == {"success": True, "conflicts": []} and not calls
    assert review_spec_consistency(SPECS)["success"] is False and len(calls) == 1
    calls = _llm(monkeypatch, "not json")
    assert review_spec_consistency(SPECS)["success"] is False and len(calls) == 1


def test_verification_models_say_whether_test_and_code_are_independent(monkeypatch):
    """Verify the summary states honestly whether one model wrote both the test and the code.

    id: TST-REV-012
    Given: The same model, then different models, for the test and code stages
    When: The verification models are read
    Then: independent is False, then True
    """
    from service_layer import services
    for var in ("LLM_MODEL_RED_TEST_GENERATION", "LLM_MODEL_GREEN_CODE_REPAIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LLM_MODEL", "m1")
    assert services.verification_models() == {"test": "m1", "code": "m1", "independent": False}
    monkeypatch.setenv("LLM_MODEL_RED_TEST_GENERATION", "m2")
    assert services.verification_models() == {"test": "m2", "code": "m1", "independent": True}


ACTIONS = {"settle_line": "`settle_line(line: whole_number)`: settles the line; when every line is settled the order "
                          "is settled"}


def _rule(i, given, then, situation):
    return BusinessSpec(spec_id=f"S{i}", title=f"T{i}", description="d", target_aggregate="Order", action="settle_line",
                        given_when_then=f"Given {given}, When settle_line(line 2), Then {then}", situation=situation)


PLANNED = [_rule(1, "one_line_open", "the order is settled", "`one_line_open`: an order of two lines, the first settled"),
           _rule(2, "one_line_open", "the order stays open", "`one_line_open`: an order of two lines, the first settled"),
           BusinessSpec(spec_id="S3", title="T3", description="d", target_aggregate="Order",
                        given_when_then="Given an order, When the page opens, Then its lines are listed")]


def _checked(*holds):
    return [{"spec": f"S{i}", "closing": "0 lines left open: met", "leaves": "the order is settled", "holds": held}
            for i, held in enumerate(holds, start=1)]


def test_each_rule_is_read_with_what_the_plan_says_its_action_does(monkeypatch):
    """Verify the review is shown the plan: an action as described, and the situation each of its rules starts from.

    id: TST-REV-013
    Given: Two rules about one action of the plan and a rule about none
    When: The set is reviewed with the plan's actions
    Then: One call held to the review's schema; its prompt gives the action as the plan describes it, each rule
          under it with the situation it starts from, and the rule about no action apart
    """
    import json
    from onboarding import spec_review
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: seen.append((p, stage, k))
                        or json.dumps({"checked": _checked(True, True), "conflicts": []}))

    result = review_spec_consistency(PLANNED, actions=ACTIONS)

    (prompt, stage, options), = seen
    assert result == {"success": True, "conflicts": []}
    assert stage == "spec_consistency_review" and options["json_schema"] is spec_review.REVIEW_SCHEMA
    assert ACTIONS["settle_line"] in prompt and "an order of two lines, the first settled" in prompt
    assert prompt.index(ACTIONS["settle_line"]) < prompt.index("- S1 [T1]") < prompt.index("- S2 [T2]")
    assert prompt.index("- S2 [T2]") < prompt.index(spec_review.NO_ACTION) < prompt.index("- S3 [T3]")


def test_a_check_marked_as_not_holding_that_no_conflict_names_is_not_reported(monkeypatch):
    """Verify one rule is reported against the plan only when the worked check and the conclusion agree.

    Measured on seven contracts: every rule that really contradicted its plan was named in a conflict too, and the
    one check marked as not holding with no conflict written for it had worked out exactly what the rule states.

    id: TST-REV-014
    Given: A model whose check of one rule says it does not hold, and which reports no conflict
    When: The set is reviewed
    Then: Nothing is reported
    """
    import json
    _llm(monkeypatch, json.dumps({"checked": _checked(True, False), "conflicts": []}))

    assert review_spec_consistency(PLANNED, actions=ACTIONS) == {"success": True, "conflicts": []}


def test_the_reason_the_model_gave_for_a_rule_that_does_not_hold_is_kept(monkeypatch):
    """Verify a conflict the model wrote about the rule is the one reported, once.

    id: TST-REV-015
    Given: A check that says one rule does not hold, a conflict naming it with a reason in everyday words, and a
           conflict naming one rule that does hold
    When: The set is reviewed
    Then: The first is reported as written and nothing is added; the second is not a conflict
    """
    import json
    said = [{"specs": ["S2"], "reason": "Settling the last line settles the order, and this rule keeps it open."},
            {"specs": ["S1"], "reason": "nothing"}]
    _llm(monkeypatch, json.dumps({"checked": _checked(True, False), "conflicts": said}))

    assert review_spec_consistency(PLANNED, actions=ACTIONS)["conflicts"] == said[:1]


def test_one_rule_is_still_reviewed_against_the_plan(monkeypatch):
    """Verify a single rule skips the review only when there is no plan to check it against.

    id: TST-REV-016
    Given: One rule and the plan's actions
    When: It is reviewed
    Then: The call is made
    """
    import json
    calls = _llm(monkeypatch, json.dumps({"checked": _checked(True), "conflicts": []}))

    assert review_spec_consistency(PLANNED[:1], actions=ACTIONS)["success"] is True and len(calls) == 1
