"""
The wiring of an app that exists: its routers and API clients, written again by today's generator.

Both are written from the decomposition alone and never by a model (`skeleton_builder.generate_router_module`,
`generate_master_client`), so writing them again loses nothing. This is how a correction to the generator reaches an
app without building the app again: the domain classes, the page and the saved records are left as they are.
"""

import os
from typing import Dict, List

from onboarding.router_engine import DomainStructureSchema
from onboarding.skeleton_builder import _to_snake_case, generate_master_client, generate_router_module
from pipeline_trace import traced


def wiring_files(structure: DomainStructureSchema) -> Dict[str, str]:
    """Every router and API client the generator writes for this decomposition, by its path in the app."""
    files: Dict[str, str] = {}
    for entity in structure.entities:
        slug = _to_snake_case(entity.name)
        files[f"src/entrypoints/routers/{slug}.py"] = generate_router_module(entity)
        files[f"src/api/{slug}Client.ts"] = generate_master_client(entity)
    return files


@traced("wiring.refresh")
def refresh_wiring(structure: DomainStructureSchema, workspace_dir: str) -> List[str]:
    """Writes again each router and client the app has that differs from the generator's, and returns their paths.
    A file the app does not have is not added: which classes have a client is the page's decision."""
    rewritten: List[str] = []
    for rel, code in wiring_files(structure).items():
        path = os.path.join(workspace_dir, *rel.split("/"))
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            current = f.read()
        if current != code:
            with open(path, "w", encoding="utf-8") as f:
                f.write(code)
            rewritten.append(rel)
    return rewritten
