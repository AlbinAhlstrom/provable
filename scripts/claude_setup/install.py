#!/usr/bin/env python3
"""Install the Claude Code project configuration into <repo>/.claude.

usage: python scripts/claude_setup/install.py [--force]

Copies scripts/claude_setup/claude/** to .claude/**. Files that already exist and
differ are left alone unless --force is given. Safe to re-run.
"""
import argparse
import filecmp
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "claude"
TARGET = HERE.parent.parent / ".claude"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="overwrite files that differ")
    args = parser.parse_args()

    if not SOURCE.is_dir():
        print(f"missing source folder: {SOURCE}", file=sys.stderr)
        return 1

    counts = {"installed": 0, "unchanged": 0, "skipped": 0, "updated": 0}
    for src in sorted(p for p in SOURCE.rglob("*") if p.is_file()):
        rel = src.relative_to(SOURCE)
        dst = TARGET / rel
        if not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            counts["installed"] += 1
            print(f"installed  .claude/{rel.as_posix()}")
        elif filecmp.cmp(src, dst, shallow=False):
            counts["unchanged"] += 1
        elif args.force:
            shutil.copy2(src, dst)
            counts["updated"] += 1
            print(f"updated    .claude/{rel.as_posix()}")
        else:
            counts["skipped"] += 1
            print(f"skipped    .claude/{rel.as_posix()} (differs; use --force to overwrite)")

    print("\n" + ", ".join(f"{n} {label}" for label, n in counts.items()))
    print("Next: start Claude Code in the project root, then check /permissions, /hooks, /agents and the skills list.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
