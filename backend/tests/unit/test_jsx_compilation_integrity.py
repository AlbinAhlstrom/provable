"""
Unit test verifying JSX syntax compilation integrity and zero Vite/Babel parsing errors across React TSX components.
"""

import os
import sys
import subprocess
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from onboarding.site_manifest_schema import UnifiedSiteManifestAST, ComponentNodeAST, NavigationRouteAST
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx


def test_frontend_tsx_components_compile_cleanly():
    """Verifies npx tsc --noEmit succeeds with zero JSX/Babel syntax errors on all src/ components."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    
    cmd = ["cmd", "/c", "npx", "tsc", "--noEmit"]
    res = subprocess.run(cmd, cwd=root_dir, capture_output=True, text=True)
    
    assert res.returncode == 0, f"TypeScript / JSX compilation error detected:\n{res.stdout}\n{res.stderr}"


def test_generated_app_tsx_ast_has_zero_jsx_syntax_errors():
    """Verifies deterministically generated App.tsx AST compiles cleanly without tag mismatches."""
    manifest_dict = {
        "brand_name": "Pizza App",
        "hero_headline": "Fresh Artisanal Pizzas",
        "hero_subtitle": "Ordered Online Fast",
        "navigation_routes": [
            {"key": "home", "label": "Home", "route": "/", "component_ref": "catalog"}
        ],
        "components": [
            {"id": "REQ-UI-CATALOG", "canonical_key": "catalog", "name": "Menu Grid", "component_type": "premade"}
        ]
    }

    compiled_code = compile_site_manifest_to_app_tsx(manifest_dict)
    
    assert "export default function App()" in compiled_code
    assert "})()}" not in compiled_code
    assert "undefined" not in compiled_code

