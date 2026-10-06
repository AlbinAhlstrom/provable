import pytest
"""Serverless (Vercel) mode: read-only checkout, so the workspace must move to a scratch directory."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import config_loader


def test_not_serverless_by_default(monkeypatch):
    """Verify local runs are unaffected.

    id: TST-VC-001
    Given: No VERCEL environment variable
    When: is_serverless is evaluated
    Then: It is False
    """
    monkeypatch.delenv("VERCEL", raising=False)
    assert config_loader.is_serverless() is False


@pytest.mark.real_workspace_resolution
def test_serverless_workspace_is_a_writable_scratch_dir(monkeypatch, tmp_path):
    """Verify the workspace moves to a temp dir on Vercel instead of the read-only checkout.

    id: TST-VC-002
    Given: VERCEL=1 and no explicit PROVABLE_WORKSPACE
    When: The active workspace base is resolved
    Then: It is a writable scratch directory outside the repository, with a requirements/ folder
    """
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.delenv("PROVABLE_WORKSPACE", raising=False)
    monkeypatch.setattr("tempfile.gettempdir", lambda: str(tmp_path))
    ws = config_loader.get_workspace_base()
    assert ws == os.path.join(str(tmp_path), "provable-workspace")
    assert os.path.isdir(os.path.join(ws, "requirements")) and os.access(ws, os.W_OK)


def test_explicit_workspace_still_wins_on_serverless(monkeypatch, tmp_path):
    """Verify an explicit workspace override is respected even on Vercel.

    id: TST-VC-003
    Given: VERCEL=1 and PROVABLE_WORKSPACE pointing at a directory
    When: The workspace base is resolved
    Then: The override is returned
    """
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("PROVABLE_WORKSPACE", str(tmp_path))
    assert config_loader.get_workspace_base() == os.path.abspath(str(tmp_path))
