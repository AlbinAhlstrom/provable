"""The generated app may import packages the scaffold must declare and the engine must install."""

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold, ensure_workspace_dependencies


def _declared(ws: str, dev: bool = False) -> dict:
    with open(os.path.join(ws, "package.json"), encoding="utf-8") as f:
        pkg = json.load(f)
    return {**pkg.get("dependencies", {}), **(pkg.get("devDependencies", {}) if dev else {})}


def test_scaffold_declares_the_icon_library_generated_apps_import(tmp_path):
    """Verify the scaffold's package.json declares lucide-react.

    id: TST-WSDEP-001
    Given: A freshly written workspace scaffold
    When: The package.json dependencies are read
    Then: lucide-react is declared, because the presentation prompts and the skeleton import it
    """
    create_default_workspace_scaffold(str(tmp_path))
    assert "lucide-react" in _declared(str(tmp_path))


def test_install_runs_only_when_a_declared_package_is_missing(tmp_path):
    """Verify npm install is skipped when everything declared is already in node_modules.

    id: TST-WSDEP-002
    Given: A scaffold whose declared packages are missing, then present, in node_modules
    When: ensure_workspace_dependencies runs each time
    Then: The installer is invoked the first time and not the second
    """
    ws = str(tmp_path)
    create_default_workspace_scaffold(ws)
    calls = []

    assert ensure_workspace_dependencies(ws, runner=lambda cwd: calls.append(cwd)) is True
    assert calls == [ws]

    for name in _declared(ws, dev=True):
        os.makedirs(os.path.join(ws, "node_modules", *name.split("/")), exist_ok=True)

    assert ensure_workspace_dependencies(ws, runner=lambda cwd: calls.append(cwd)) is False
    assert calls == [ws]
