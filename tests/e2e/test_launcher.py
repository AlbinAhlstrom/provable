import sys
import os
import pytest

# Add root directory to sys.path
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import run


@pytest.mark.e2e
def test_launcher_environment_constants():
    """Verify run.py environment constants and path resolution."""
    assert run.ROOT == root_path
    assert isinstance(run.IS_WINDOWS, bool)
    assert run.processes == []
