"""
Canary Test - No Legacy Ghosts Zone.
Recursively inspects all frontend/src/ TypeScript files to ensure zero resurrection
of hardcoded pizza or legacy e-commerce UI mocks.
"""
import os
import pytest

FORBIDDEN_TOKENS = ["Pizza", "Signature Industrial", "AppCraft"]

def test_no_legacy_ghosts_in_frontend_src():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "frontend", "src"))
    assert os.path.exists(root_dir), f"Frontend src directory not found at {root_dir}"

    violations = []
    for dir_path, _, filenames in os.walk(root_dir):
        for fn in filenames:
            if fn.endswith(".ts") or fn.endswith(".tsx"):
                file_path = os.path.join(dir_path, fn)
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for token in FORBIDDEN_TOKENS:
                        if token.lower() in content.lower():
                            violations.append(f"{fn} contains forbidden legacy token: '{token}'")

    if violations:
        nl = chr(10)
        raise AssertionError(f"Legacy code resurrection detected. Revert your changes. Violations:\n" + "\n".join(violations))
