"""
AST & Code Syntax Verifier with Self-Healing Closed Loop.

Parses React TSX code for structural balance and syntax errors before saving to disk.
If syntax errors are detected, triggers a targeted self-healing LLM repair step.
"""

from pipeline_trace import traced
import re
import sys
import os
from dataclasses import dataclass
from typing import Callable, Dict, Any, Sequence, Tuple, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import agent_orchestrator
from agent_orchestrator import call_gemini
from onboarding.page_parts import MISSING
from onboarding.qa_opening_check import EMPTY
from onboarding.verification import compile_tsx


def verify_tsx_syntax(code: str) -> Tuple[bool, str]:
    """
    Validates React TSX syntax by checking bracket balance, JSX tag pairing,
    and required default export declaration.
    Returns (is_valid, error_message).
    """
    if not code or not isinstance(code, str):
        return False, "Code string is empty or invalid"

    clean_code = code.strip()

    # 1. Export check
    if "export default" not in clean_code and "App" not in clean_code:
        return False, "Missing React component export declaration (export default App)"

    # 2. Basic bracket balancing check
    stack = []
    pairs = {'{': '}', '(': ')', '[': ']'}
    
    # Strip strings & comments for bracket checking
    code_no_strings = re.sub(r'\'[^\']*\'|"[^"]*"|`[^`]*`', '', clean_code)
    code_no_comments = re.sub(r'//.*?\n|/\*.*?\*/', '', code_no_strings, flags=re.DOTALL)

    for char in code_no_comments:
        if char in pairs:
            stack.append(pairs[char])
        elif char in ('}', ')', ']'):
            if not stack or stack.pop() != char:
                return False, f"Unbalanced bracket mismatch near '{char}'"

    if stack:
        return False, f"Unclosed bracket: expected '{stack[-1]}'"

    # 3. Check for HTML/JSX root element
    if not re.search(r'<[a-zA-Z][^>]*>', clean_code):
        return False, "No valid JSX element found in component render output"

    return True, "Syntax OK"


def self_heal_tsx_code(code: str, error_msg: str, pitch: str) -> str:
    """
    Closed-loop repair step: sends the broken TSX code and compiler error
    back to Gemini for automatic self-healing.
    """
    prompt = agent_orchestrator.load_prompt("self_healing.md", {
        "error_message": error_msg,
        "business_pitch": pitch,
        "broken_code": code
    })
    try:
        repaired = call_gemini(prompt, stage="self_healing")
        if repaired and "export default" in repaired:
            cleaned = repaired.strip()
            fence_match = re.search(r'```(?:tsx|jsx|typescript|javascript)?\s*\n(.*?)```', cleaned, re.DOTALL)
            if fence_match:
                cleaned = fence_match.group(1).strip()
            
            is_valid, _ = verify_tsx_syntax(cleaned)
            if is_valid:
                print("✨ [self_heal_tsx_code] Successfully self-healed TSX compilation error!")
                return cleaned
    except Exception as e:
        print(f"⚠️ [self_heal_tsx_code] Self-healing step failed: {e}")

    return code


_FILE_MARKER = re.compile(r"^<<<([^<>\n]+)>>>[ \t]*$", re.MULTILINE)


@dataclass(frozen=True)
class FileFix:
    """One repaired component: its path relative to the workspace (e.g. src/App.tsx) and its full new source."""
    path: str
    code: str


@dataclass(frozen=True)
class PresentationRepair:
    """The healer's typed answer: a replacement for each component that needs one."""
    fixes: List[FileFix]

    @classmethod
    def from_response(cls, raw: str) -> "PresentationRepair":
        """Reads `<<<src/...>>>` file blocks closed by `<<<end>>>`: plain source, as the page writer answers. A whole
        file escaped into a JSON string proved fragile (one lost escape and the file no longer compiles)."""
        marks = list(_FILE_MARKER.finditer(raw or ""))
        if not marks:
            raise ValueError(f"no <<<file>>> markers in the answer; it began: {(raw or '')[:200]!r}")
        fixes = []
        for mark, following in zip(marks, marks[1:] + [None]):
            path = mark.group(1).strip()
            if path == "end":
                break
            code = raw[mark.end():following.start() if following else len(raw)].strip()
            if not code:
                raise ValueError(f"the block for {path} is empty")
            fixes.append(FileFix(path=path, code=code))
        return cls(fixes=fixes)


def _component_index(workspace_dir: str, component_files: List[str]) -> Dict[str, List[str]]:
    """Maps each generated component's workspace-relative path (src/...) to every on-disk copy of it."""
    roots = [os.path.abspath(os.path.join(workspace_dir, "src")),
             os.path.abspath(os.path.join(workspace_dir, "frontend", "src"))]
    index: Dict[str, List[str]] = {}
    for file_path in component_files:
        absolute = os.path.abspath(file_path)
        for root in roots:
            if absolute.startswith(root + os.sep):
                rel = "src/" + os.path.relpath(absolute, root).replace(os.sep, "/")
                if absolute not in index.setdefault(rel, []):
                    index[rel].append(absolute)
    return index


@traced("qa.self_heal")
def self_heal_presentation_suite(
    workspace_dir: str,
    pitch: str,
    defects: List[str],
    console_errors: List[str],
    component_files: List[str],
    contract_files: Sequence[str] = (),
    compile_check: Callable[[str, str], Tuple[bool, str]] = compile_tsx,
    plan: str = "",
) -> bool:
    """
    Closed-loop LLM repair for live preview issues detected by the QA auditor.
    The model sees every generated component plus the defects and returns a typed
    PresentationRepair naming the files to replace; only generated components are writable.
    `contract_files` (the API clients, written from the domain model) are shown and stay as they are: the page is
    changed to fit them. A fix that does not compile is not written, so the file keeps what it had.
    `plan` is the page's plan: a defect that names a part the page lacks is answered from it.
    One call, no retry. Returns True if at least one file was repaired.
    """
    if not defects and not console_errors:
        return False

    fixed = _component_index(workspace_dir, list(contract_files))
    index = {rel: copies for rel, copies in _component_index(workspace_dir, component_files).items() if rel not in fixed}
    if not index:
        return False

    combined_errors = "\n".join([f"- Defect: {d}" for d in defects] + [f"- Console Error: {ce}" for ce in console_errors])
    sources = []
    for rel, copies in index.items():
        try:
            with open(copies[0], "r", encoding="utf-8") as f:
                sources.append(f"--- FILE ({rel}) ---\n{f.read()}")
        except OSError as e:
            print(f"⚠️ [self_heal_presentation_suite] Could not read {copies[0]}: {e}", flush=True)
            return False
    contracts = []
    for rel, copies in fixed.items():
        try:
            with open(copies[0], "r", encoding="utf-8") as f:
                contracts.append(f"--- FILE ({rel}) ---\n{f.read()}")
        except OSError:
            continue
    contract_block = ("\n--- THE API CLIENTS (fixed: written from the domain model; the components are changed to fit "
                      "them, and a request the API refuses is shown to the user as it is) ---\n"
                      + "\n".join(contracts) + "\n") if contracts else ""

    plan_block = ("\n--- THE PAGE'S PLAN (a defect that names a missing part, or a page that opens empty, is answered from this "
                  "plan: a part by its role, its name, what brings it up and what it does; the opening by its section) ---\n"
                  + plan + "\n") if plan and any(MISSING in d or EMPTY in d for d in defects) else ""

    prompt = f"""You are Provable's Principal Lead Frontend Architect.
The live application preview on :5174 failed runtime verification.

--- OBJECTIVE RUNTIME DEFECTS & BROWSER LOGS ---
{combined_errors}

--- PRODUCT PITCH ---
{pitch}

--- GENERATED COMPONENTS ---
{chr(10).join(sources)}
{contract_block}{plan_block}
Task:
1. Diagnose which component(s) cause the defects above; layout defects usually carry no file name, so decide from the code.
2. Fix syntax, JSX escaping, prop mismatches or layout scaling so the app renders cleanly without errors. `App.tsx` must keep `export default App;`.
3. Keep user-facing copy natural and persona-focused (no internal compiler terms like Invariant, Audit Ledger, Boundary Guards).
4. Change only the files that need it, and in them only what answers a defect: what no defect names stays exactly as it is (its colours, sizes, copy and behaviour), since it was measured and passed.

Answer with one block for each file you change: its marker alone on a line, `<<<` + one of the FILE paths above + `>>>`,
then the complete corrected file as plain source text (no JSON, no escaping, no fences, no commentary). After the last
file write the marker `<<<end>>>` alone on a line. For example:

<<<src/App.tsx>>>
(the complete corrected file)
<<<end>>>
"""
    try:
        raw = call_gemini(prompt, stage="self_healing", json_mode=False)
        repair = PresentationRepair.from_response(raw)
    except Exception as e:
        print(f"⚠️ [self_heal_presentation_suite] Self-healing failed: {e} ({agent_orchestrator.LAST_LLM_ERROR or 'no provider error'})", flush=True)
        return False

    healed = []
    for fix in repair.fixes:
        copies = index.get(fix.path)
        if not copies:
            print(f"⚠️ [self_heal_presentation_suite] Refused fix for non-component path {fix.path!r}", flush=True)
            continue
        compiles, verdict = compile_check(workspace_dir, fix.code)
        if not compiles:
            print(f"⚠️ [self_heal_presentation_suite] Refused fix for {fix.path}: it does not compile ({verdict})", flush=True)
            continue
        for p in copies:
            with open(p, "w", encoding="utf-8") as f:
                f.write(fix.code.strip() + "\n")
        healed.append(fix.path)

    if healed:
        print(f"✨ [self_heal_presentation_suite] Healed {', '.join(healed)} via LLM closed loop!", flush=True)
    return bool(healed)

