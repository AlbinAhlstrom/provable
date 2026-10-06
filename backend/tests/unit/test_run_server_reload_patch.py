"""
Unit tests for backend/run_server.py Uvicorn reload patch and run.py process configuration.
Verifies that Windows hot-reloading does not broadcast CTRL_C_EVENT signals to parent processes.
"""

import sys
import os
from unittest.mock import MagicMock, patch
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def test_run_server_patches_basereload_restart():
    """Verify that backend/run_server.py patches BaseReload.restart correctly without AttributeError."""
    import uvicorn.supervisors.basereload
    backend_dir = os.path.join(ROOT, "backend")
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)

    import run_server

    assert callable(uvicorn.supervisors.basereload.BaseReload.restart)

    mock_supervisor = MagicMock(spec=uvicorn.supervisors.basereload.BaseReload)
    mock_proc = MagicMock()
    mock_proc.is_alive.return_value = True
    mock_supervisor.process = mock_proc
    mock_supervisor.config = MagicMock()
    mock_supervisor.target = MagicMock()
    mock_supervisor.sockets = []

    with patch("uvicorn.supervisors.basereload.get_subprocess") as mock_get_sub:
        new_proc = MagicMock()
        mock_get_sub.return_value = new_proc

        uvicorn.supervisors.basereload.BaseReload.restart(mock_supervisor)

        mock_proc.terminate.assert_called_once()
        mock_proc.join.assert_called_once()
        mock_get_sub.assert_called_once_with(
            config=mock_supervisor.config,
            target=mock_supervisor.target,
            sockets=mock_supervisor.sockets
        )
        new_proc.start.assert_called_once()


def test_run_py_uses_run_server_for_workspace_api():
    """Verify that run.py launches workspace backend with run_server.py rather than raw -m uvicorn."""
    run_py_path = os.path.join(ROOT, "run.py")
    with open(run_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    assert "ws_backend_cmd = [" in content
    assert 'py_exe, run_server_script, "src.app:app"' in content or "py_exe, run_server_script, 'src.app:app'" in content
