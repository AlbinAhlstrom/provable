"""Unit tests for the single-file TSX compile check (backend/onboarding/verification.py: compile_tsx)."""

import os
import subprocess
from types import SimpleNamespace

import pytest

from onboarding import verification
from onboarding.verification import compile_tsx

_FRONTEND = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend"))


def _fake_run(stdout="", returncode=0, stderr="", raises=None):
    def run(*args, **kwargs):
        if raises:
            raise raises
        return SimpleNamespace(stdout=stdout, stderr=stderr, returncode=returncode)
    return run


def test_the_compilers_verdict_is_returned(monkeypatch):
    """Verify the check reports the compiler's own words.

    id: TST-TSX-001
    Given: A compiler that accepts one source and rejects another
    When: Each is checked
    Then: The first is ok; the second is refused with the compiler's message
    """
    monkeypatch.setattr(subprocess, "run", _fake_run(stdout="OK"))
    assert compile_tsx("ws", "export const A = 1") == (True, "")
    monkeypatch.setattr(subprocess, "run", _fake_run(stdout='ERR Unexpected "null" (line 15: actionError: string null;)'))
    assert compile_tsx("ws", "x") == (False, 'Unexpected "null" (line 15: actionError: string null;)')


def test_a_compiler_that_cannot_run_is_a_refusal_with_the_reason(monkeypatch):
    """Verify code that could not be checked is never reported as checked.

    id: TST-TSX-002
    Given: No node on the machine, then a compiler process that dies
    When: A source is checked
    Then: Both are refusals that say the compiler could not run
    """
    monkeypatch.setattr(subprocess, "run", _fake_run(raises=FileNotFoundError("node")))
    ok, reason = compile_tsx("ws", "x")
    assert ok is False and "could not run" in reason
    monkeypatch.setattr(subprocess, "run", _fake_run(returncode=1, stderr="Cannot find module 'esbuild'"))
    ok, reason = compile_tsx("ws", "x")
    assert ok is False and "could not run" in reason and "esbuild" in reason


@pytest.mark.slow
@pytest.mark.skipif(not os.path.isdir(os.path.join(_FRONTEND, "node_modules", "esbuild")), reason="needs frontend/node_modules")
def test_the_real_compiler_catches_what_bracket_counting_cannot():
    """Verify the check runs a real TSX compiler.

    id: TST-TSX-003
    Given: A component, and the same component with the `|` of a union type missing
    When: Both are compiled with the esbuild that ships with Vite
    Then: The first compiles; the second is refused naming the offending line
    """
    good = "interface P { error: string | null }\nexport const A = (p: P) => <div>{p.error}</div>;\n"
    assert compile_tsx(_FRONTEND, good) == (True, "")
    ok, reason = compile_tsx(_FRONTEND, good.replace("string | null", "string null"))
    assert ok is False and "line 1" in reason
    assert verification.compile_tsx is compile_tsx
