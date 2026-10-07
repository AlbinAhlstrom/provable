"""QA rework repairs the component the model names, chosen from the generated files (no regex guess)."""

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding import code_verifier
from onboarding.code_verifier import FileFix, PresentationRepair, self_heal_presentation_suite


@pytest.fixture
def workspace(tmp_path):
    for root in ("src", os.path.join("frontend", "src")):
        for rel, body in {"App.tsx": "APP", "views/BoardView.tsx": "BOARD"}.items():
            path = tmp_path / root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body, encoding="utf-8")
    return tmp_path


def _components(ws):
    return [str(ws / "src" / "App.tsx"), str(ws / "src" / "views" / "BoardView.tsx"),
            str(ws / "frontend" / "src" / "App.tsx"), str(ws / "frontend" / "src" / "views" / "BoardView.tsx")]


def _answer(*fixes):
    return json.dumps({"fixes": [{"path": p, "code": c} for p, c in fixes]})


def test_contract_parses_a_json_answer():
    repair = PresentationRepair.from_response(_answer(("src/App.tsx", "x")))
    assert repair.fixes == [FileFix(path="src/App.tsx", code="x")]


def test_contract_rejects_malformed_answer():
    with pytest.raises(ValueError):
        PresentationRepair.from_response(json.dumps({"fixes": [{"path": "src/App.tsx"}]}))


def test_layout_defect_without_file_repairs_the_file_the_model_names(workspace, monkeypatch):
    seen = {}

    def fake(prompt, stage="general", json_mode=False, **kw):
        seen.update(prompt=prompt, stage=stage, json_mode=json_mode)
        return _answer(("src/views/BoardView.tsx", "FIXED"))

    monkeypatch.setattr(code_verifier, "call_gemini", fake)
    healed = self_heal_presentation_suite(str(workspace), "pitch", ["horizontal overflow at 375px"], [],
                                          component_files=_components(workspace))
    assert healed is True
    assert seen["stage"] == "self_healing" and seen["json_mode"] is True
    assert "BOARD" in seen["prompt"] and "APP" in seen["prompt"]  # the model sees every component
    assert (workspace / "src/views/BoardView.tsx").read_text().strip() == "FIXED"
    assert (workspace / "frontend/src/views/BoardView.tsx").read_text().strip() == "FIXED"  # mirrored
    assert (workspace / "src/App.tsx").read_text() == "APP"  # untouched


def test_paths_outside_the_generated_components_are_refused(workspace, monkeypatch):
    monkeypatch.setattr(code_verifier, "call_gemini",
                        lambda *a, **k: _answer(("src/Evil.tsx", "x"), ("../escape.tsx", "x")))
    assert self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace)) is False
    assert not (workspace / "src" / "Evil.tsx").exists()
    assert not (workspace.parent / "escape.tsx").exists()


def test_unparseable_answer_fails_without_retry(workspace, monkeypatch):
    calls = []
    monkeypatch.setattr(code_verifier, "call_gemini", lambda *a, **k: calls.append(1) or "not json")
    assert self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace)) is False
    assert len(calls) == 1


def test_nothing_to_heal_makes_no_call(workspace, monkeypatch):
    monkeypatch.setattr(code_verifier, "call_gemini", lambda *a, **k: pytest.fail("called"))
    assert self_heal_presentation_suite(str(workspace), "p", [], [], component_files=_components(workspace)) is False
