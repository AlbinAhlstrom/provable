"""A plan whose review names rules is sent back once, for those rules alone (onboarding/plan_rework.py), before
anything is built from it (onboarding/kickstart_front.py)."""
import copy
import json

import pytest

import agent_orchestrator
from onboarding import kickstart_front as kf
from onboarding import plan_rework as pr
from onboarding import product_contract as pc
from test_product_contract import CONTRACT

TITLE = "A booking holds its table"
CONFLICTS = [{"specs": ["SPEC-001"], "reason": "Booking the only free table leaves none, and the rule says one is left."}]
LARGER = "three_tables_free = three tables and nobody has booked: Table 1 with seats 2, Table 2 and Table 3 with seats 4"
REWRITTEN = {"title": TITLE, "given": "three_tables_free", "when": "create_booking(table_id of Table 1, guests 2)",
             "then": "a Booking with status confirmed; two tables stay free", "sees": "\"Table 1, taken\"",
             "plain": "Given three free tables, When a guest books one, Then two are still free"}


def _contract() -> pc.ProductContract:
    return pc.ProductContract.from_dict(copy.deepcopy(CONTRACT))


def _answers(monkeypatch, answer):
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini",
                        lambda prompt, stage="general", **k: calls.append((prompt, stage, k)) or answer)
    return calls


def test_the_named_rules_are_rewritten_and_everything_else_of_the_plan_is_as_it_was(monkeypatch):
    """
    Given: A plan, a review that named one of its rules, and a writer that answers with that rule rewritten from a
           new, larger situation
    When: The plan is reworked
    Then: One call for the stage `plan_rework`, held to its schema, whose prompt holds the plan, the rule and what the
          review found; the rule has its new clauses and keeps its action and feature; the new situation is added;
          every other rule, the situations there were and the actions are untouched; the plan given is not changed
    """
    before = _contract()
    calls = _answers(monkeypatch, json.dumps({"situations": [LARGER], "rules": [REWRITTEN]}))

    after = pr.rework_rules(before, CONFLICTS)

    (prompt, stage, options), = calls
    assert stage == "plan_rework" and options["json_schema"] is pr.REWORK_SCHEMA
    assert TITLE in prompt and CONFLICTS[0]["reason"] in prompt and "creates a Booking with status confirmed" in prompt
    rule = after.rules[0]
    assert (rule.given, rule.then, rule.plain) == (REWRITTEN["given"], REWRITTEN["then"], REWRITTEN["plain"])
    assert (rule.action, rule.title) == ("create_booking", TITLE)
    assert after.specs()[0].situation.startswith("`three_tables_free`: three tables")
    assert after.situations == before.situations + [LARGER]
    assert after.rules[1:] == before.rules[1:] and after.actions == before.actions
    assert after.source["rules"][0]["then"] == REWRITTEN["then"]
    assert before.rules[0].given == "two_tables_free" and before.source["rules"][0]["given"] == "two_tables_free"


@pytest.mark.parametrize("answer, reason", [
    ("", "APITimeoutError"),
    ("not json", "not valid JSON"),
    (json.dumps({"situations": [], "rules": []}), "no rule"),
    (json.dumps({"situations": [], "rules": [{**REWRITTEN, "title": "No more than eight guests"}]}), "was not named"),
    (json.dumps({"situations": ["two_tables_free = one table"], "rules": [REWRITTEN]}), "two_tables_free"),
    (json.dumps({"situations": [], "rules": [{**REWRITTEN, "given": "a full house"}]}), "starts from no situation"),
])
def test_a_rework_that_was_not_delivered_fails_with_the_reason(monkeypatch, answer, reason):
    """
    Given: A writer that answers nothing, no JSON, no rule, a rule the review did not name, a situation other rules
           already start from, or a rule that starts from no situation of the plan
    When: The plan is reworked
    Then: It fails by name with the reason, after one call
    """
    calls = _answers(monkeypatch, answer)
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "APITimeoutError: timed out", raising=False)

    with pytest.raises(pr.ReworkError, match=reason):
        pr.rework_rules(_contract(), CONFLICTS)
    assert len(calls) == 1


def test_the_writer_is_held_to_write_at_least_one_rule():
    """Verify the provider is held to write a rule back: once, the answer added the situations the named rules needed
    and closed the list of rules empty, and the plan was built with the rules the review had found could not hold.

    id: TST-REWORK-SCHEMA-NONEMPTY
    Given: The schema the rework is answered in
    When: Its lists are read
    Then: The rules hold at least one entry; the situations may be none
    """
    lists = pr.REWORK_SCHEMA["properties"]
    assert lists["rules"].get("minItems") == 1
    assert lists["situations"].get("minItems") is None


def _front(monkeypatch, review, rework):
    monkeypatch.setattr(pc, "write_product_contract", lambda pitch: _contract())
    return kf.contract_front("A table booking page", review=review, rework=rework)


def _never(*args, **kwargs):
    raise AssertionError("must not be called")


def test_a_plan_the_review_finds_nothing_in_is_built_as_written_and_reviewed_once(monkeypatch):
    """
    Given: A plan whose review finds no conflict
    When: The front of a kickstart is built
    Then: The review read the plan's rules once, nothing was rewritten, and the build's review stage answers with
          what was found, without another call
    """
    reviews = []
    clean = {"success": True, "conflicts": []}

    front = _front(monkeypatch, review=lambda specs, intent=None: reviews.append(specs) or clean, rework=_never)

    assert len(reviews) == 1 and [s.title for s in reviews[0]] == [r["title"] for r in CONTRACT["rules"]]
    monkeypatch.setattr(agent_orchestrator, "call_gemini", _never)
    assert front.stage_overrides()["review"](front.inbox_specs, intent=front.intent) is clean
    assert front.inbox_specs[0].situation.startswith("`two_tables_free`")


def test_a_plan_the_review_names_rules_in_is_sent_back_once_before_anything_is_built(monkeypatch):
    """
    Given: A plan whose review names a rule, and a rework that corrects it
    When: The front of a kickstart is built
    Then: The rework was given the plan and what the review found, once; the rule deck, the stored specification and
          the contract kept are the corrected ones; and the build's review stage reads the corrected rules anew
    """
    found, reworks = {"success": True, "conflicts": CONFLICTS}, []
    corrected = pr.applied(_contract(), {"situations": [LARGER], "rules": [REWRITTEN]}, {TITLE})

    front = _front(monkeypatch, review=lambda specs, intent=None: found,
                   rework=lambda contract, conflicts: reworks.append(conflicts) or corrected)

    assert reworks == [CONFLICTS] and front.contract is corrected
    assert front.inbox_specs[0].given_when_then.startswith("Given three_tables_free")
    assert "three_tables_free" in front.pitch_text and "three_tables_free" in front.stored_pitch
    seen = {}
    from onboarding import spec_review
    monkeypatch.setattr(spec_review, "review_spec_consistency",
                        lambda specs, intent=None, actions=None: seen.update(specs=specs) or {"success": True, "conflicts": []})
    assert front.stage_overrides()["review"](front.inbox_specs)["conflicts"] == [] and seen["specs"] is front.inbox_specs


def test_a_rework_that_fails_leaves_the_plan_as_written_and_the_conflicts_reported(monkeypatch):
    """
    Given: A plan whose review names a rule, and a rework that fails
    When: The front of a kickstart is built
    Then: The plan is built as it was written, nothing is tried again, and the build's review stage still reports
          what the review found
    """
    found, tried = {"success": True, "conflicts": CONFLICTS}, []

    def rework(contract, conflicts):
        tried.append(1)
        raise pr.ReworkError("the answer rewrote no rule")

    front = _front(monkeypatch, review=lambda specs, intent=None: found, rework=rework)

    assert tried == [1] and front.inbox_specs[0].given_when_then.startswith("Given two_tables_free")
    assert front.stage_overrides()["review"](front.inbox_specs) is found


def test_a_review_that_fails_is_not_run_again_and_nothing_is_rewritten(monkeypatch):
    """
    Given: A review that fails (a provider error)
    When: The front of a kickstart is built
    Then: The plan is built as written, no rework is tried, and the build's review stage reports the failure without
          another call
    """
    failed = {"success": False, "error": "APITimeoutError"}

    front = _front(monkeypatch, review=lambda specs, intent=None: failed, rework=_never)

    monkeypatch.setattr(agent_orchestrator, "call_gemini", _never)
    assert front.stage_overrides()["review"](front.inbox_specs) is failed
