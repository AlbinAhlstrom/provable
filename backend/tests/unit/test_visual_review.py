"""Unit tests for the visual review (backend/onboarding/visual_review.py): look once, repair only what looks wrong."""

import json

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


def _review(tmp_path, answer, audit=None, compiles=(True, ""), calls=None):
    view, shots = _workspace(tmp_path)

    def llm(prompt, stage="general", **options):
        if calls is not None:
            calls.append({"prompt": prompt, "stage": stage, **options})
        return answer if isinstance(answer, str) else json.dumps(answer)

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
