"""Unit tests for the visual review (backend/onboarding/visual_review.py): look once, repair only what looks wrong."""

import json
import os

import pytest

from onboarding import visual_review
from onboarding.visual_review import ClassEdit, apply_class_edit, review_and_repair

_VIEW = """import React from 'react';
export const View = ({ active }: { active: boolean }) => (
  <main className="bg-slate-500 p-2">
    <h1 className={`text-xl ${active ? 'bg-slate-500' : 'bg-white'}`}>Our p-2 plan is bg-slate-500</h1>
    <p className="text-sm p-20">Details</p>
  </main>
);
"""


def _edit(find, replace, file="src/views/View.tsx", problem="grey page"):
    return ClassEdit(problem=problem, file=file, find=find, replace=replace)


def test_a_class_edit_changes_classes_and_nothing_else():
    """Verify a repair reaches class attributes only: copy that happens to contain the same words is untouched.

    id: TST-VR-001
    Given: A component where a class name also appears in visible text and inside a conditional class expression
    When: The class is replaced
    Then: Both class occurrences change, the visible text does not, and a longer class that merely starts the same is kept
    """
    code, count, reason = apply_class_edit(_VIEW, _edit("bg-slate-500", "bg-amber-50"))
    assert (count, reason) == (2, "")
    assert 'className="bg-amber-50 p-2"' in code and "'bg-amber-50' : 'bg-white'" in code
    assert "Our p-2 plan is bg-slate-500" in code
    code, count, _ = apply_class_edit(_VIEW, _edit("p-2", "p-6"))
    assert count == 1 and 'className="bg-slate-500 p-6"' in code and "p-20" in code and "Our p-2 plan" in code


@pytest.mark.parametrize("find, replace, expected", [
    ("bg-rose-900", "bg-amber-50", "not found"),
    ("bg-slate-500", 'bg-white" onClick={steal}', "only class names"),
    ("bg-slate-500", "bg-slate-500", "changes nothing"),
    ("", "bg-white", "only class names"),
])
def test_an_edit_that_cannot_be_applied_safely_is_refused_with_the_reason(find, replace, expected):
    """Verify a repair can never smuggle in code, and a miss is reported instead of ignored.

    id: TST-VR-002
    Given: Edits whose class is absent, whose replacement contains code, or that change nothing
    When: Each is applied
    Then: The code is unchanged and the reason says why
    """
    code, count, reason = apply_class_edit(_VIEW, _edit(find, replace))
    assert code == _VIEW and count == 0 and expected in reason


def _workspace(tmp_path):
    view = tmp_path / "src" / "views" / "View.tsx"
    view.parent.mkdir(parents=True)
    view.write_text(_VIEW, encoding="utf-8")
    shot = tmp_path / "desktop.png"
    shot.write_bytes(b"png")
    return view, {"desktop": str(shot)}


def _review(tmp_path, answer, audit=None, compiles=(True, ""), calls=None, retry_answer=None):
    """`answer` is the review; `retry_answer` is what the model says when refused repairs are sent back (nothing new
    by default)."""
    view, shots = _workspace(tmp_path)
    answers = [answer, retry_answer if retry_answer is not None else {"problems": []}]
    if calls is None:
        calls = []

    def llm(prompt, stage="general", **options):
        calls.append({"prompt": prompt, "stage": stage, **options})
        given = answers[min(len(calls), len(answers)) - 1]
        return given if isinstance(given, str) else json.dumps(given)

    result = review_and_repair(
        workspace_dir=str(tmp_path), pitch="p", visual_direction="warm cream page, one amber accent",
        component_files=[str(view)], screenshots=shots, audit=audit, llm=llm, compile_check=lambda ws, code: compiles)
    return view, result


def test_a_page_with_nothing_wrong_is_left_alone(tmp_path):
    """Verify the common case costs one look and changes nothing.

    id: TST-VR-003
    Given: A review that reports no problems
    When: The page is reviewed
    Then: The verdict is clean, no file changes, the model saw the screenshots and the direction, and no audit is re-run
    """
    calls, audits = [], []
    view, result = _review(tmp_path, {"problems": []}, audit=lambda: audits.append(1) or {"passed": True}, calls=calls)
    assert result["verdict"] == "clean" and result["edits"] == [] and audits == []
    assert view.read_text(encoding="utf-8") == _VIEW
    assert calls[0]["images"] == [str(tmp_path / "desktop.png")] and calls[0]["stage"] == "visual_review"
    assert "warm cream page" in calls[0]["prompt"] and "bg-slate-500 p-2" in calls[0]["prompt"]


def test_a_reported_problem_is_repaired_and_the_page_is_audited_again(tmp_path):
    """Verify a repair is applied, reported edit by edit, and proven by a fresh audit.

    id: TST-VR-004
    Given: A review with one class repair, one repair whose class is not in the file and one problem without a repair
    When: The page is reviewed
    Then: The first is applied, the other two are listed as not repaired with reasons, and the audit ran once
    """
    audits = []
    answer = {"problems": [
        {"problem": "grey page background", "file": "src/views/View.tsx", "find": "bg-slate-500", "replace": "bg-amber-50"},
        {"problem": "weak button", "file": "src/views/View.tsx", "find": "bg-rose-900", "replace": "bg-amber-700"},
        {"problem": "the hero has no image", "file": None, "find": None, "replace": None}]}
    view, result = _review(tmp_path, answer, audit=lambda: audits.append(1) or {"passed": True, "defects": []})
    assert result["verdict"] == "repaired" and audits == [1]
    assert "bg-amber-50" in view.read_text(encoding="utf-8")
    applied = [e for e in result["edits"] if e["applied"]]
    assert len(applied) == 1 and applied[0]["occurrences"] == 2
    assert sorted(result["not_repaired"]) == ["the hero has no image: no class change can fix it",
                                              "weak button: the class text was not found in src/views/View.tsx"]


def test_repairs_that_break_the_page_are_taken_back(tmp_path):
    """Verify a repair never leaves the page worse: a failed compile or a failed audit restores the files.

    id: TST-VR-005
    Given: A repair after which the component does not compile, then one after which the audit finds a defect
    When: The page is reviewed
    Then: Both times the file is as it was and the verdict says why
    """
    answer = {"problems": [{"problem": "grey", "file": "src/views/View.tsx", "find": "bg-slate-500", "replace": "bg-amber-50"}]}
    view, result = _review(tmp_path / "a", answer, compiles=(False, "Unexpected token"))
    assert view.read_text(encoding="utf-8") == _VIEW and result["verdict"] == "unrepaired"
    assert "Unexpected token" in result["edits"][0]["reason"]

    view, result = _review(tmp_path / "b", answer, audit=lambda: {"passed": False, "defects": ["[Mobile] 40px overflow"]})
    assert view.read_text(encoding="utf-8") == _VIEW and result["verdict"] == "reverted"
    assert "40px overflow" in result["error"]


@pytest.mark.parametrize("answer, expected", [("", "empty response"), ("not json", "not a usable review")])
def test_a_review_that_cannot_be_read_fails_loudly_and_is_not_retried(tmp_path, answer, expected):
    """Verify provider and parse errors are reported, never retried and never mistaken for a clean page.

    id: TST-VR-006
    Given: A model that returns nothing, then text that is not JSON
    When: The page is reviewed
    Then: One call is made, the verdict is error with the reason, and no file changes
    """
    import agent_orchestrator
    agent_orchestrator.LAST_LLM_ERROR = None  # the fake model reports no provider error
    calls = []
    view, result = _review(tmp_path, answer, calls=calls)
    assert len(calls) == 1 and result["verdict"] == "error" and expected in result["error"]
    assert view.read_text(encoding="utf-8") == _VIEW


def test_the_review_prompt_asks_for_class_changes_only():
    """Verify the prompt states the contract the parser enforces.

    id: TST-VR-007
    Given: The visual review prompt
    When: It is read
    Then: It names the JSON fields and says a page with nothing wrong returns an empty list
    """
    import agent_orchestrator
    body = agent_orchestrator.load_prompt(visual_review.REVIEW_PROMPT)
    assert all(field in body for field in ('"problems"', '"find"', '"replace"', '"file"'))
    assert "empty list" in body


def test_the_review_is_shown_the_records_and_reports_a_claim_no_record_carries(tmp_path):
    """Verify the one look before shipping also reads what the page says about the business against its records.

    id: TST-VR-008
    Given: A workspace with seed records, and a review that lists two claims no record carries and no visual problem
    When: The page is reviewed
    Then: The model was shown the records, the claims are in the result under their own key, and no file changes
    """
    seed = tmp_path / "src" / "seed_data.json"
    seed.parent.mkdir(parents=True)
    seed.write_text(json.dumps({"Profile": [{"id": "a", "name": "Ada Lind"}]}), encoding="utf-8")
    view = tmp_path / "src" / "views" / "View.tsx"
    view.parent.mkdir(parents=True)
    view.write_text(_VIEW, encoding="utf-8")
    shot = tmp_path / "desktop.png"
    shot.write_bytes(b"png")
    calls = []

    def llm(prompt, stage="general", **options):
        calls.append(prompt)
        return json.dumps({"problems": [], "claims": ["Fully insured", "Every sitter is background checked"]})

    result = review_and_repair(workspace_dir=str(tmp_path), pitch="p", visual_direction="d", component_files=[str(view)],
                               screenshots={"desktop": str(shot)}, llm=llm, compile_check=lambda ws, code: (True, ""))
    assert "Ada Lind" in calls[0]
    assert result["verdict"] == "clean" and result["claims"] == ["Fully insured", "Every sitter is background checked"]
    assert view.read_text(encoding="utf-8") == _VIEW


def test_the_review_prompt_asks_about_claims_the_records_do_not_carry():
    """id: TST-VR-009
    Given: The visual review prompt
    When: It is read
    Then: It has a place for the records and asks for statements about the business that no record carries
    """
    import agent_orchestrator
    body = open(os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "visual_review.md"), encoding="utf-8").read()
    assert "{records}" in body and "no record carries" in body and '"claims"' in body
    assert "under a heading" in body  # a sub-heading that describes the business is a claim too


_CONDITION = "active ? 'bg-slate-500' : 'bg-white'"


def test_a_refused_repair_is_sent_back_once_with_the_reason(tmp_path):
    """Verify the one retry the policy allows: the applier refused a repair, and its verdict goes back to the reviewer.

    id: TST-VR-RETRY-001
    Given: A review whose repair copies a whole condition instead of class names, and a second answer that gives the
           classes alone
    When: The page is reviewed
    Then: Two calls are made; the second is told which repair was refused and why; the corrected repair is applied
          and the result says two attempts were made
    """
    calls = []
    first = {"problems": [{"problem": "pale heading", "file": "src/views/View.tsx", "find": _CONDITION, "replace": "active ? 'bg-slate-900' : 'bg-white'"}]}
    second = {"problems": [{"problem": "pale heading", "file": "src/views/View.tsx", "find": "bg-white", "replace": "bg-slate-900"}]}
    view, result = _review(tmp_path, first, calls=calls, retry_answer=second)

    assert len(calls) == 2 and result["attempts"] == 2 and result["verdict"] == "repaired"
    assert "the edit must hold only class names" in calls[1]["prompt"] and _CONDITION in calls[1]["prompt"]
    assert calls[1]["images"] == calls[0]["images"]
    assert "'bg-slate-900'" in view.read_text(encoding="utf-8") and result["not_repaired"] == []


def test_a_repair_refused_twice_is_reported_and_never_tried_a_third_time(tmp_path):
    """Verify the retry is exactly one.

    id: TST-VR-RETRY-002
    Given: A review whose repair is refused, and a second answer that is refused the same way
    When: The page is reviewed
    Then: Two calls are made, nothing changes, and the problem is listed as not repaired with the reason
    """
    calls = []
    bad = {"problems": [{"problem": "pale heading", "file": "src/views/View.tsx", "find": _CONDITION, "replace": "x ? 'a' : 'b'"}]}
    view, result = _review(tmp_path, bad, calls=calls, retry_answer=bad)

    assert len(calls) == 2 and result["verdict"] == "unrepaired" and view.read_text(encoding="utf-8") == _VIEW
    assert result["not_repaired"] == ["pale heading: the edit must hold only class names"]


def test_a_corrected_repair_answers_its_problem_however_the_reviewer_words_it(tmp_path):
    """Verify a problem repaired on the retry is not also reported as left on the page.

    id: TST-VR-RETRY-004
    Given: Two refused repairs, and a second answer that describes both problems in other words: one with a repair
           that applies, one refused again
    When: The page is reviewed
    Then: The repaired problem is not listed as not repaired; the other is listed once, under its new wording
    """
    first = {"problems": [
        {"problem": "pale heading", "file": "src/views/View.tsx", "find": _CONDITION, "replace": "active ? 'bg-slate-900' : 'bg-white'"},
        {"problem": "grey button", "file": "src/views/View.tsx", "find": _CONDITION, "replace": "x ? 'a' : 'b'"}]}
    second = {"problems": [
        {"problem": "the heading is hard to read", "file": "src/views/View.tsx", "find": "bg-white", "replace": "bg-slate-900"},
        {"problem": "the button looks disabled", "file": "src/views/View.tsx", "find": _CONDITION, "replace": "x ? 'a' : 'b'"}]}
    view, result = _review(tmp_path, first, retry_answer=second)

    assert result["verdict"] == "repaired" and "'bg-slate-900'" in view.read_text(encoding="utf-8")
    assert result["not_repaired"] == ["the button looks disabled: the edit must hold only class names"]


def test_no_second_call_when_no_repair_was_refused(tmp_path):
    """Verify the retry is only ever an answer to a refusal.

    id: TST-VR-RETRY-003
    Given: A review with one repair that applies and one problem it says no class change can fix
    When: The page is reviewed
    Then: One call is made
    """
    calls = []
    answer = {"problems": [
        {"problem": "grey page background", "file": "src/views/View.tsx", "find": "bg-slate-500", "replace": "bg-amber-50"},
        {"problem": "the hero has no image", "file": None, "find": None, "replace": None}]}
    _, result = _review(tmp_path, answer, calls=calls)
    assert len(calls) == 1 and result["attempts"] == 1


def test_what_the_review_saw_and_could_not_repair_is_a_reported_failure():
    """Verify a visible problem left on the page is not a silent note in the log.

    id: TST-VR-UNRESOLVED
    Given: A clean review, a review that repaired everything, one that left a problem, and one whose repairs were taken back
    When: Each is asked what it leaves unresolved
    Then: The first two leave nothing; the others name the problem or the reason
    """
    assert visual_review.unresolved({"verdict": "clean", "not_repaired": [], "error": None}) == ""
    assert visual_review.unresolved({"verdict": "repaired", "not_repaired": [], "error": None}) == ""
    left = visual_review.unresolved({"verdict": "unrepaired", "not_repaired": ["white pieces are invisible: the edit must hold only class names"], "error": None})
    assert "white pieces are invisible" in left
    assert "no longer passed QA" in visual_review.unresolved(
        {"verdict": "reverted", "not_repaired": [], "error": "the repairs were taken back, the page no longer passed QA: overflow"})


def test_the_prompts_say_how_to_repair_classes_inside_a_condition_and_ask_for_contrast_on_every_background():
    """Verify the two prompts state what this run got wrong.

    id: TST-VR-PROMPTS
    Given: The visual review prompt and the presentation prompt
    When: They are read
    Then: The review prompt says which text to copy when classes sit inside a condition; the presentation prompt asks
          that each owner's things keep one colour of their own, readable on each background they land on; the
          reviewer looks for owners that cannot be told apart
    """
    import agent_orchestrator
    prompts = os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts")
    review = open(os.path.join(prompts, "visual_review.md"), encoding="utf-8").read()
    page = open(os.path.join(prompts, "presentation_projection_synthesis.md"), encoding="utf-8").read()
    assert "inside a condition" in review and "one of its quoted strings" in review
    assert "stays the same wherever the thing is placed" in page and "readable on each" in page and "uFE0E" in page
    assert "Telling things apart" in review


def test_the_reviewer_is_told_what_was_measured_and_repaired_before_it_looked(tmp_path):
    """Verify the review does not undo a repair that answered a measured defect.

    id: TST-VR-SETTLED
    Given: A page whose unreadable text was repaired after QA measured it, and a page with nothing settled
    When: Each is reviewed
    Then: The first prompt quotes the settled defect and says what answers it stays; the second says nothing was settled
    """
    view, shots = _workspace(tmp_path)
    prompts = []

    def llm(prompt, **options):
        prompts.append(prompt)
        return json.dumps({"problems": []})

    for settled in (["Unreadable text: drawn in #ffffff on a background of #fde68a"], []):
        review_and_repair(workspace_dir=str(tmp_path), pitch="p", visual_direction="d", component_files=[str(view)],
                          screenshots=shots, llm=llm, compile_check=lambda ws, code: (True, ""), settled=settled)
    assert "drawn in #ffffff on a background of #fde68a" in prompts[0] and "stays as it is" in prompts[0]
    assert "(nothing)" in prompts[1]
