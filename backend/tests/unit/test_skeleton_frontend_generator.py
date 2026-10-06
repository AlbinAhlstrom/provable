"""
Unit tests for full-stack frontend generator in skeleton_builder.py.
Verifies that Provable generates a standalone Vite + React 18 + Tailwind frontend in workspace/frontend/.
"""

import pytest
import os
from onboarding.router_engine import DomainStructureSchema, EntitySpec, AttributeSpec
from onboarding.skeleton_builder import generate_fullstack_skeleton_files


def test_generate_fullstack_skeleton_includes_frontend():
    entities = [
        EntitySpec(
            name="Pallet",
            attributes=[
                AttributeSpec(name="id", type="str", required=True),
                AttributeSpec(name="weight", type="float", default_value=0.0),
                AttributeSpec(name="status", type="str", default_value="AVAILABLE")
            ]
        ),
        EntitySpec(
            name="Zone",
            attributes=[
                AttributeSpec(name="id", type="str", required=True),
                AttributeSpec(name="capacity", type="int", default_value=10),
                AttributeSpec(name="is_quarantined", type="bool", default_value=False)
            ]
        )
    ]
    structure = DomainStructureSchema(domain_name="WarehouseManagement", entities=entities, value_objects=[])

    files = generate_fullstack_skeleton_files(structure, base_path="workspace")


    # Verify standard backend files
    assert any(f.endswith(os.path.join("src", "domain", "pallet.py")) for f in files)
    assert any(f.endswith(os.path.join("src", "domain", "zone.py")) for f in files)
    assert any(f.endswith(os.path.join("src", "app.py")) for f in files)

    # Verify standalone frontend files
    frontend_files = [f for f in files if "frontend" in f]
    assert len(frontend_files) >= 8, f"Expected frontend files, found: {frontend_files}"

    # Verify core frontend config & source
    package_json = next(c for p, c in files.items() if p.endswith("package.json"))
    assert "warehousemanagement" in package_json or "workspace-frontend" in package_json
    assert "react" in package_json
    assert "vite" in package_json


    vite_config = next(c for p, c in files.items() if p.endswith("vite.config.ts"))
    assert "5174" in vite_config
    assert "8001" in vite_config

    api_client = next(c for p, c in files.items() if p.endswith(os.path.join("src", "api", "client.ts")))
    assert "fetchPalletList" in api_client
    assert "fetchZoneList" in api_client

    app_tsx = next(c for p, c in files.items() if p.endswith(os.path.join("src", "App.tsx")))
    assert "PalletView" in app_tsx
    assert "ZoneView" in app_tsx

    pallet_view = next(c for p, c in files.items() if p.endswith(os.path.join("src", "views", "PalletView.tsx")))
    assert "Pallet Management" in pallet_view or "Pallet" in pallet_view
