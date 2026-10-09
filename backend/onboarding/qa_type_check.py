"""
QA type check: the page is held to its own types.

The preview compiles each file on its own and drops the types, so a page that reads a field its own code never set
(or one the API client does not declare) still renders, with that part of it empty. The TypeScript compiler sees the
contradiction in seconds, without a browser.

- Each error the compiler reports in the sources is a defect, quoted with its file, lines and the compiler's own
  message, so the one rework knows what to change. The same message in one file is one defect.
- A compiler that could not run (not installed, timed out, failed without naming a source error) is a warning: the
  check's limit, not the page's fault.
"""

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Callable, Dict, List

from pipeline_trace import traced

TIMEOUT_S = 60
MAX_DEFECTS = 12
_ERROR = re.compile(r"^(?P<file>[^\s(][^(]*)\((?P<line>\d+),\d+\): error TS\d+: (?P<message>.+)$")


@dataclass
class TypeCheck:
    """What the compiler said about the page. Defects fail the audit; warnings are reported with the verdict."""
    defects: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def defects_from_output(output: str) -> List[str]:
    """One defect per message per file, in the compiler's order, with every line the message was reported on."""
    lines_of: Dict[tuple, List[str]] = {}
    for raw in (output or "").splitlines():
        found = _ERROR.match(raw.strip())
        if found:
            key = (found["file"].replace("\\", "/"), found["message"].strip())
            lines_of.setdefault(key, []).append(found["line"])
    return [f"[Types] {file} line{'s' if len(lines) > 1 else ''} {', '.join(lines)}: {message[:400]}"
            for (file, message), lines in list(lines_of.items())[:MAX_DEFECTS]]


@traced("qa.type_check")
def check_types(workspace_dir: str, run: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> TypeCheck:
    """Runs the workspace's own TypeScript compiler over its sources, writing nothing."""
    npx_cmd = "npx.cmd" if os.name == "nt" else "npx"
    try:
        res = run([npx_cmd, "--no-install", "tsc", "--noEmit", "-p", "."], cwd=workspace_dir, capture_output=True,
                  text=True, encoding="utf-8", timeout=TIMEOUT_S)
    except Exception as err:  # missing compiler, timeout: report, do not guess
        return TypeCheck(warnings=[f"the type check could not run: {type(err).__name__}: {str(err)[:200]}"])
    if res.returncode == 0:
        return TypeCheck()
    output = (res.stdout or "") + (res.stderr or "")
    defects = defects_from_output(output)
    if not defects:
        return TypeCheck(warnings=[f"the type check could not run: {output.strip()[-300:]}"])
    return TypeCheck(defects=defects)
