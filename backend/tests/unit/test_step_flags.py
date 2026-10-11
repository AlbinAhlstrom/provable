"""A step says what looked wrong in what it was given, and does its task all the same (onboarding/step_flags.py).

A code writer that found a frozen test wrong once answered in words where code was expected, and a class lost every
rule with it. A step has one channel for such a doubt: a marked line in its answer, which code takes out, records
and routes. What to do about it is never the step's decision.
"""
import json
import os

import pytest

import run_recorder
from onboarding import step_flags
from onboarding.step_flags import Flag

ANSWER = '''# FLAG test_spec_003.py: expects a paid invoice to take a line; the rule refuses it
from dataclasses import dataclass

  # FLAG tests/unit/test_spec_007.py: arranges a total of 90 and calls it 120
@dataclass
class Invoice:
    # flagged lines are comments like any other only when they carry the mark
    total: int = 0
'''


@pytest.fixture
def runs_root(monkeypatch, tmp_path):
    root = tmp_path / "runs"
    monkeypatch.setenv("PROVABLE_RUNS_DIR", str(root))
    monkeypatch.delenv("PROVABLE_RECORD_RUNS", raising=False)
    monkeypatch.delenv("PROVABLE_TRACE_DIR", raising=False)
    return root


def test_flag_lines_are_taken_out_of_an_answer():
    """Verify the flags are read as data and the answer is left as the step's ordinary output.

    id: TST-FLAG-001
    Given: A code answer with two flag lines, one indented and one naming its test by path
    When: The flags are taken
    Then: Both are returned with the step, what they are about and what they say; the answer holds neither line
          and everything else, the ordinary comment included
    """
    answer, flags = step_flags.take("green_code_repair", ANSWER)

    assert flags == [
        Flag("green_code_repair", "test_spec_003.py", "expects a paid invoice to take a line; the rule refuses it"),
        Flag("green_code_repair", "tests/unit/test_spec_007.py", "arranges a total of 90 and calls it 120")]
    assert "FLAG" not in answer and "# flagged lines are comments" in answer
    compile(answer, "answer", "exec")


def test_an_answer_without_flags_is_returned_as_it_is():
    """Verify the ordinary case costs nothing.

    id: TST-FLAG-002
    Given: An answer with no flag line
    When: The flags are taken
    Then: The answer is unchanged and there are no flags
    """
    assert step_flags.take("green_code_repair", "class Invoice:\n    total: int = 0\n") == (
        "class Invoice:\n    total: int = 0\n", [])


def test_a_flag_is_kept_in_the_runs_summary_and_trace(runs_root, tmp_path):
    """Verify a flag can be found after the run without reading every answer.

    id: TST-FLAG-003
    Given: A recorded run in which a step's answer carries a flag
    When: The run ends
    Then: summary.json lists the flag with its step, and the trace holds an entry for it
    """
    with run_recorder.recorded_run("kickstart", "p", workspace_dir=str(tmp_path)):
        step_flags.take("green_code_repair", ANSWER)

    run = next(p for p in runs_root.iterdir() if p.is_dir())
    summary = json.loads((run / "summary.json").read_text(encoding="utf-8"))
    assert summary["flags"][0] == {"step": "green_code_repair", "about": "test_spec_003.py",
                                   "says": "expects a paid invoice to take a line; the rule refuses it"}
    assert len(summary["flags"]) == 2
    assert any("step.flags" in name for name in os.listdir(run / "trace"))
