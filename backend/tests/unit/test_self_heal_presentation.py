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


def _compiles(workspace_dir, code):
    return ("BROKEN" not in code, "Unterminated regular expression. (line 61)")


def _answer(*fixes):
    return "".join(f"<<<{p}>>>\n{c}\n" for p, c in fixes) + "<<<end>>>\n"


def test_contract_parses_file_blocks_carrying_code_verbatim():
    """Verify the rework answers in plain source, as the page writer does.

    id: TST-HEAL-BLOCKS
    Given: An answer of two file blocks with quotes, braces and backslashes in the code, closed by the end marker
    When: It is parsed
    Then: Each file's code is exactly what was written between its marker and the next; text after the end is dropped
    """
    code = 'const s = "q\\"uote"; export const App = () => <div style={{ a: 1 }} />;'
    repair = PresentationRepair.from_response(_answer(("src/App.tsx", code), ("src/views/BoardView.tsx", "x")) + "Done.")
    assert repair.fixes == [FileFix(path="src/App.tsx", code=code), FileFix(path="src/views/BoardView.tsx", code="x")]


def test_an_end_marker_after_each_file_keeps_every_file():
    """Verify a rework that closes each file with the end marker loses none of them.

    id: TST-HEAL-BLOCKS-EACH-END
    Given: An answer that writes `<<<end>>>` after every file block, as a live rework did, with prose after the last
    When: It is parsed
    Then: Every file is read, each exactly as written; what follows an end marker outside a block is dropped
    """
    answer = ("Both files fixed.\n\n<<<src/App.tsx>>>\nAPP\n<<<end>>>\n\n"
              "<<<src/views/BoardView.tsx>>>\nBOARD\n<<<end>>>\n\n<<<end>>>\n")
    repair = PresentationRepair.from_response(answer)
    assert repair.fixes == [FileFix(path="src/App.tsx", code="APP"), FileFix(path="src/views/BoardView.tsx", code="BOARD")]


def test_contract_rejects_malformed_answer():
    for bad in ("just prose", "<<<src/App.tsx>>>\n\n<<<end>>>"):
        with pytest.raises(ValueError):
            PresentationRepair.from_response(bad)


def test_layout_defect_without_file_repairs_the_file_the_model_names(workspace, monkeypatch):
    seen = {}

    def fake(prompt, stage="general", json_mode=False, **kw):
        seen.update(prompt=prompt, stage=stage, json_mode=json_mode)
        return _answer(("src/views/BoardView.tsx", "FIXED"))

    monkeypatch.setattr(code_verifier, "call_gemini", fake)
    healed = self_heal_presentation_suite(str(workspace), "pitch", ["horizontal overflow at 375px"], [],
                                          component_files=_components(workspace), compile_check=_compiles)
    assert healed is True
    assert seen["stage"] == "self_healing" and seen["json_mode"] is False
    assert "<<<end>>>" in seen["prompt"]
    assert "BOARD" in seen["prompt"] and "APP" in seen["prompt"]  # the model sees every component
    assert (workspace / "src/views/BoardView.tsx").read_text().strip() == "FIXED"
    assert (workspace / "frontend/src/views/BoardView.tsx").read_text().strip() == "FIXED"  # mirrored
    assert (workspace / "src/App.tsx").read_text() == "APP"  # untouched


def test_paths_outside_the_generated_components_are_refused(workspace, monkeypatch):
    monkeypatch.setattr(code_verifier, "call_gemini",
                        lambda *a, **k: _answer(("src/Evil.tsx", "x"), ("../escape.tsx", "x")))
    assert self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace), compile_check=_compiles) is False
    assert not (workspace / "src" / "Evil.tsx").exists()
    assert not (workspace.parent / "escape.tsx").exists()


def test_unparseable_answer_fails_without_retry(workspace, monkeypatch):
    calls = []
    monkeypatch.setattr(code_verifier, "call_gemini", lambda *a, **k: calls.append(1) or "no blocks here")
    assert self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace), compile_check=_compiles) is False
    assert len(calls) == 1


def test_nothing_to_heal_makes_no_call(workspace, monkeypatch):
    monkeypatch.setattr(code_verifier, "call_gemini", lambda *a, **k: pytest.fail("called"))
    assert self_heal_presentation_suite(str(workspace), "p", [], [], component_files=_components(workspace), compile_check=_compiles) is False


def test_a_fix_that_does_not_compile_is_not_written(workspace, monkeypatch):
    """Verify the rework cannot leave the page worse than it found it.

    id: TST-HEAL-COMPILE
    Given: An answer with one fix that compiles and one that does not
    When: The rework is applied
    Then: The file whose fix compiles is replaced; the other keeps what it had, in every copy
    """
    monkeypatch.setattr(code_verifier, "call_gemini", lambda *a, **k: _answer(
        ("src/App.tsx", "BETTER"), ("src/views/BoardView.tsx", "BROKEN <div")))
    assert self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace),
                                        compile_check=_compiles) is True
    assert (workspace / "src/App.tsx").read_text().strip() == "BETTER"
    assert (workspace / "src/views/BoardView.tsx").read_text() == "BOARD"
    assert (workspace / "frontend/src/views/BoardView.tsx").read_text() == "BOARD"


def test_the_api_clients_are_shown_but_cannot_be_rewritten(workspace, monkeypatch):
    """Verify the page is changed to fit the API's client, never the client to fit the page.

    id: TST-HEAL-CONTRACT
    Given: A generated API client beside the components, and an answer that rewrites it
    When: The rework is applied
    Then: The model saw the client, marked as fixed; the client keeps its content and nothing was repaired
    """
    client = workspace / "src" / "api" / "boardClient.ts"
    client.parent.mkdir(parents=True)
    client.write_text("CLIENT", encoding="utf-8")
    seen = {}

    def fake(prompt, **kw):
        seen["prompt"] = prompt
        return _answer(("src/api/boardClient.ts", "MOCK"))

    monkeypatch.setattr(code_verifier, "call_gemini", fake)
    healed = self_heal_presentation_suite(str(workspace), "p", ["d"], [], component_files=_components(workspace) + [str(client)],
                                          contract_files=[str(client)], compile_check=_compiles)
    assert healed is False
    assert client.read_text() == "CLIENT"
    fixed_part = seen["prompt"].split("--- THE API CLIENTS")[1]
    assert "CLIENT" in fixed_part and "BOARD" not in fixed_part


def test_the_rework_is_asked_to_leave_what_no_defect_names(tmp_path, monkeypatch):
    """Verify a repair of one colour does not move the colours beside it.

    id: TST-HEAL-SCOPE
    Given: A page with a defect
    When: The rework is asked for a fix
    Then: The prompt says that what no defect names stays exactly as it is
    """
    import inspect
    from onboarding import code_verifier
    source = inspect.getsource(code_verifier.self_heal_presentation_suite)
    assert "what no defect names stays exactly as it is" in source
