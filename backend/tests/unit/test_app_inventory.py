"""Unit tests for the generated-frontend inventory (backend/onboarding/app_inventory.py)."""

from onboarding.app_inventory import inventory_frontend


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_files_the_served_app_never_imports_are_reported_as_unreachable(tmp_path):
    """Verify dead generated files are visible (a 440-line component nothing imported shipped unnoticed).

    id: TST-INV-001
    Given: main.tsx imports App, App imports a view and a client, and two more components exist that nothing imports
    When: The frontend is inventoried
    Then: The imported chain is reachable, the other two are listed as unreachable, each with its line count
    """
    _write(tmp_path, "src/main.tsx", "import * as AppModule from './App';\nimport './index.css';\n")
    _write(tmp_path, "src/index.css", "body {}\n")
    _write(tmp_path, "src/App.tsx", "import { View } from './views/View';\nimport { list } from './api/client';\nexport default View;\n")
    _write(tmp_path, "src/views/View.tsx", "import React from 'react';\nexport const View = () => null;\n")
    _write(tmp_path, "src/api/client.ts", "export const list = () => [];\n")
    _write(tmp_path, "src/components/Controls/Dead.tsx", "export const Dead = () => null;\n" * 3)
    _write(tmp_path, "src/views/Unused.tsx", "import { Dead } from '../components/Controls/Dead';\n")
    _write(tmp_path, "src/domain/model.py", "x = 1\n")  # the backend is not part of the frontend

    inventory = inventory_frontend(str(tmp_path))

    by_path = {f.path: f for f in inventory.files}
    assert set(by_path) == {"src/main.tsx", "src/index.css", "src/App.tsx", "src/views/View.tsx", "src/api/client.ts",
                            "src/components/Controls/Dead.tsx", "src/views/Unused.tsx"}
    assert [f.path for f in inventory.unreachable()] == ["src/components/Controls/Dead.tsx", "src/views/Unused.tsx"]
    assert by_path["src/App.tsx"].reachable and by_path["src/App.tsx"].lines == 3
    assert by_path["src/components/Controls/Dead.tsx"].lines == 3
    report = inventory.to_dict()
    assert report["unreachable"] == ["src/components/Controls/Dead.tsx", "src/views/Unused.tsx"]
    assert report["reachable_lines"] == 2 + 1 + 3 + 2 + 1 and report["unreachable_lines"] == 4


def test_a_workspace_without_an_entry_point_reports_nothing_reachable(tmp_path):
    """Verify a missing entry point is stated, not mistaken for an app with no dead files.

    id: TST-INV-002
    Given: A workspace with a component but no src/main.tsx
    When: The frontend is inventoried
    Then: The entry is reported missing and the component is unreachable
    """
    _write(tmp_path, "src/App.tsx", "export default null;\n")
    inventory = inventory_frontend(str(tmp_path))
    assert inventory.entry_found is False
    assert [f.path for f in inventory.unreachable()] == ["src/App.tsx"]
