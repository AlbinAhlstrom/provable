"""Inventory of the generated frontend: every source file under `src/`, how long it is, and whether the served app
reaches it.

The preview serves `src/main.tsx` and whatever that imports. Anything else under `src/` is generated code nobody sees:
it costs generation time, misleads whoever reads the workspace, and is edited in vain by a later presentation spec. The
inventory makes that visible in every run's summary.

The skeleton's scaffold (a table view per entity and one shared client) is what the app shows until the presentation
stage writes the real page. Once that page is written, the scaffold it no longer imports is removed
(`remove_unreachable`), so every file left under `src/` is one the page renders.
"""

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

ENTRY = "src/main.tsx"
_SOURCE_EXTENSIONS = (".tsx", ".ts", ".jsx", ".js", ".css")
_RESOLVE_SUFFIXES = ("", ".tsx", ".ts", ".jsx", ".js", "/index.tsx", "/index.ts")
_SKIP_DIRS = {"node_modules", "__pycache__", "dist"}
# `import x from './a'`, `import './a.css'`, `export * from './a'` and `import('./a')`: relative specifiers only
_IMPORT = re.compile(r"""(?:\bfrom\s*|\bimport\s*\(?\s*)['"](\.{1,2}/[^'"]+)['"]""")


@dataclass(frozen=True)
class SourceFile:
    path: str  # workspace-relative, forward slashes
    lines: int
    reachable: bool


@dataclass(frozen=True)
class AppInventory:
    entry: str
    entry_found: bool
    files: List[SourceFile]

    def unreachable(self) -> List[SourceFile]:
        return [f for f in self.files if not f.reachable]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "entry": self.entry,
            "entry_found": self.entry_found,
            "files": {f.path: f.lines for f in self.files},
            "unreachable": [f.path for f in self.unreachable()],
            "reachable_lines": sum(f.lines for f in self.files if f.reachable),
            "unreachable_lines": sum(f.lines for f in self.unreachable()),
        }


def imports_of(source: str) -> List[str]:
    """The relative import specifiers in a source file."""
    return _IMPORT.findall(source)


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except (OSError, UnicodeDecodeError):
        return ""


def _resolve(workspace_dir: str, importer: str, specifier: str) -> Optional[str]:
    base = os.path.normpath(os.path.join(os.path.dirname(importer), specifier)).replace(os.sep, "/")
    for suffix in _RESOLVE_SUFFIXES:
        if os.path.isfile(os.path.join(workspace_dir, base + suffix)):
            return base + suffix
    return None


def inventory_frontend(workspace_dir: str, entry: str = ENTRY) -> AppInventory:
    sources: Dict[str, str] = {}
    for dirpath, dirnames, filenames in os.walk(os.path.join(workspace_dir, "src")):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            if name.endswith(_SOURCE_EXTENSIONS):
                full = os.path.join(dirpath, name)
                sources[os.path.relpath(full, workspace_dir).replace(os.sep, "/")] = _read(full)

    reached, queue = set(), [entry] if entry in sources else []
    while queue:
        current = queue.pop()
        if current in reached:
            continue
        reached.add(current)
        for specifier in imports_of(sources[current]):
            target = _resolve(workspace_dir, current, specifier)
            if target in sources and target not in reached:
                queue.append(target)

    files = [SourceFile(path=p, lines=len(sources[p].splitlines()), reachable=p in reached) for p in sorted(sources)]
    return AppInventory(entry=entry, entry_found=entry in sources, files=files)


def remove_unreachable(workspace_dir: str, entry: str = ENTRY) -> List[str]:
    """Deletes the frontend source files the served app does not reach and returns their paths. Without the entry
    file nothing can be called reachable, so nothing is removed."""
    inventory = inventory_frontend(workspace_dir, entry)
    if not inventory.entry_found:
        return []
    removed = []
    for source in inventory.unreachable():
        os.remove(os.path.join(workspace_dir, source.path))
        removed.append(source.path)
    return removed
