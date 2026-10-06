"""Unit tests for the opt-in pipeline tracer (backend/pipeline_trace.py)."""

import glob
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pipeline_trace import traced, traced_llm


@traced("unit.inner")
def _inner(x):
    return {"doubled": x * 2}


@traced("unit.outer")
def _outer(x):
    return _inner(x)["doubled"] + 1


@traced_llm
def _fake_llm(prompt, stage="general"):
    return f"echo:{prompt}"


def test_tracing_is_noop_without_trace_dir(monkeypatch, tmp_path):
    """Verify nothing is written and results are unchanged when tracing is off.

    id: TST-TR-001
    Given: PROVABLE_TRACE_DIR is unset
    When: Traced functions run
    Then: Results are returned normally and no files are created
    """
    monkeypatch.delenv("PROVABLE_TRACE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    assert _outer(2) == 5
    assert _fake_llm("hi", stage="s") == "echo:hi"
    assert list(tmp_path.iterdir()) == []


def test_tracing_records_inputs_outputs_and_nesting(monkeypatch, tmp_path):
    """Verify each step writes its input, output, depth and caller chain in call order.

    id: TST-TR-002
    Given: PROVABLE_TRACE_DIR points at a directory
    When: A traced step calls another traced step and an LLM wrapper runs
    Then: One numbered file per call exists with the expected payloads
    """
    monkeypatch.setenv("PROVABLE_TRACE_DIR", str(tmp_path))
    assert _outer(3) == 7
    _fake_llm("prompt text", stage="demo")

    entries = [json.load(open(f)) for f in sorted(glob.glob(str(tmp_path / "*.json")))]
    assert [e["step"] for e in entries] == ["unit.outer", "unit.inner", "llm.demo"]
    by_step = {e["step"]: e for e in entries}
    assert by_step["unit.outer"]["depth"] == 0
    assert by_step["unit.inner"]["depth"] == 1 and by_step["unit.inner"]["caller_chain"] == ["unit.outer"]
    assert by_step["unit.inner"]["output"] == {"doubled": 6}
    assert by_step["llm.demo"]["input"] == {"stage": "demo", "prompt": "prompt text", "options": {}}
    assert by_step["llm.demo"]["kind"] == "llm" and by_step["llm.demo"]["output"] == "echo:prompt text"
    assert entries[0]["seq"] < entries[1]["seq"]


def test_tracing_redacts_api_keys_and_records_errors(monkeypatch, tmp_path):
    """Verify secrets never reach disk and exceptions are recorded then re-raised.

    id: TST-TR-003
    Given: An API key in the environment and a step that echoes it then fails
    When: The traced step runs
    Then: The trace contains [REDACTED] instead of the key and an error entry
    """
    monkeypatch.setenv("PROVABLE_TRACE_DIR", str(tmp_path))
    monkeypatch.setenv("GEMINI_API_KEY", "super-secret-key-12345")

    @traced("unit.fail")
    def failing(token):
        raise RuntimeError(f"bad token {token}")

    try:
        failing("super-secret-key-12345")
        raised = False
    except RuntimeError:
        raised = True
    assert raised
    text = open(glob.glob(str(tmp_path / "*unit.fail.json"))[0]).read()
    assert "super-secret-key-12345" not in text
    assert "[REDACTED]" in text and "RuntimeError" in text
