"""Routers and services.py never reach the store directly; they go through a unit of work (.claude/rules/engine.md)."""
import pathlib
import re

BACKEND = pathlib.Path(__file__).resolve().parents[2]
LEAK = re.compile(r"^\s*(?:import\s+db\.store|from\s+db\.store\s+import|from\s+db\s+import\s+.*\bstore\b)", re.M)


def test_routers_and_services_do_not_import_the_store():
    files = sorted((BACKEND / "entrypoints" / "routers").glob("*.py")) + [BACKEND / "service_layer" / "services.py"]
    leaks = [str(f.relative_to(BACKEND)) for f in files if LEAK.search(f.read_text(encoding="utf-8"))]
    assert not leaks, f"import the store through a unit of work instead: {leaks}"
