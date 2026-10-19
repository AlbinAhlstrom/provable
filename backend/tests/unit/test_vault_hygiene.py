"""
The vault is the project wiki; these checks keep it from drifting away from the code.

- every [[wikilink]] resolves to a page
- vault/Home.md lists every page
- backticked source file names (`something.py`) in the architecture, workflow, testing, ADR and rules pages
  exist in the repository
- no absolute machine paths
"""
import os
import re

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
VAULT = os.path.join(REPO, "vault")

# Narrative pages that quote the book's file names rather than this repo's.
HISTORICAL = ("06-Cosmic-Python-Journey/",)
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".obsidian", "logs", "dist", ".pytest_cache"}


def _pages():
    pages = {}
    for dirpath, dirnames, filenames in os.walk(VAULT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            if name.endswith(".md"):
                full = os.path.join(dirpath, name)
                pages[os.path.relpath(full, VAULT).replace(os.sep, "/")] = full
    return pages


def _read(path):
    with open(path, encoding="utf-8-sig") as handle:
        return handle.read()


def _repo_basenames():
    names = set()
    for dirpath, dirnames, filenames in os.walk(REPO):
        # The generated app is not the repository's source: what it holds changes with every build.
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and d not in ("vault", "workspace")]
        names.update(filenames)
    return names


def test_wikilinks_resolve():
    pages = _pages()
    stems = {os.path.splitext(os.path.basename(rel))[0] for rel in pages}
    broken = []
    for rel, path in pages.items():
        for target in re.findall(r"\[\[([^\]|#]+)", _read(path)):
            if target.strip() not in stems:
                broken.append(f"{rel} -> [[{target.strip()}]]")
    assert not broken, "broken wikilinks:\n" + "\n".join(sorted(broken))


def test_home_lists_every_page():
    pages = _pages()
    home = _read(os.path.join(VAULT, "Home.md"))
    missing = [
        rel for rel in pages
        if rel != "Home.md" and f"[[{os.path.splitext(os.path.basename(rel))[0]}" not in home
    ]
    assert not missing, "pages missing from vault/Home.md:\n" + "\n".join(sorted(missing))


def test_referenced_source_files_exist():
    existing = _repo_basenames()
    stale = []
    for rel, path in _pages().items():
        if rel.startswith(HISTORICAL):
            continue
        for ref in set(re.findall(r"`([\w./-]+\.(?:py|tsx|ts|sh|tmpl))`", _read(path))):
            if os.path.basename(ref) not in existing:
                stale.append(f"{rel}: `{ref}`")
    assert not stale, "references to files that no longer exist:\n" + "\n".join(sorted(stale))


def test_no_absolute_machine_paths():
    offenders = []
    for rel, path in _pages().items():
        if rel.startswith(HISTORICAL):
            continue
        if re.search(r"file:///|[A-Za-z]:[\\/]Users[\\/]|/home/\w+/", _read(path)):
            offenders.append(rel)
    assert not offenders, "absolute machine paths in:\n" + "\n".join(sorted(offenders))
