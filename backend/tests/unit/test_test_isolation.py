"""The test session must never touch the live workspace or its database."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from config_loader import get_workspace_base
from db.store import get_db_path

LIVE_WORKSPACE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "workspace"))


def test_session_uses_throwaway_workspace_and_database():
    """Verify tests are pointed at a temp workspace and DB, not the live ones.

    id: TST-ISO-001
    Given: The pytest session started by conftest.py
    When: The active workspace base and database path are resolved
    Then: Both live outside the repository's live workspace/ directory
    """
    ws = os.path.abspath(str(get_workspace_base()))
    db = os.path.abspath(get_db_path())
    assert ws != LIVE_WORKSPACE and not ws.startswith(LIVE_WORKSPACE + os.sep)
    assert not db.startswith(LIVE_WORKSPACE + os.sep)
    assert os.path.basename(ws).startswith("provable-test-ws-")
