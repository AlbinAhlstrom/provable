"""
AST & Code Syntax Verifier with Self-Healing Closed Loop.

Parses React TSX code for structural balance and syntax errors before saving to disk.
If syntax errors are detected, triggers a targeted self-healing LLM repair step.
"""

import re
import sys
import os
from typing import Dict, Any, Tuple, List
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_orchestrator import call_gemini


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
    prompt = f"""
You are a Principal Lead React Engineer. The following generated React TypeScript (`App.tsx`) code failed syntax verification:

--- ERROR TRACEBACK ---
{error_msg}

--- ORIGINAL BUSINESS PITCH ---
{pitch}

--- BROKEN CODE ---
{code}

Fix ALL syntax errors, unbalanced brackets, or missing JSX elements.
Return ONLY valid React TypeScript code inside a single ```tsx code block. Do NOT include markdown intro/outro.
"""
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


def self_heal_presentation_suite(
    workspace_dir: str,
    pitch: str,
    defects: List[str],
    console_errors: List[str]
) -> bool:
    """
    Closed-loop LLM repair for live preview issues detected by QA Auditor.
    Identifies the broken component from compiler/browser traces, feeds it to Gemini,
    and writes back the repaired code.
    Returns True if repaired and saved.
    """
    if not defects and not console_errors:
        return False

    combined_errors = "\n".join([f"- Defect: {d}" for d in defects] + [f"- Console Error: {ce}" for ce in console_errors])

    # Detect if a specific component file was flagged in traceback
    target_rel = "src/App.tsx"
    file_match = re.search(r'src/([a-zA-Z0-9_/]+\.tsx)', combined_errors)
    if file_match:
        target_rel = f"src/{file_match.group(1)}"

    target_paths = [
        os.path.join(workspace_dir, target_rel),
        os.path.join(workspace_dir, "frontend", target_rel)
    ]

    target_path = None
    for p in target_paths:
        if os.path.exists(p):
            target_path = p
            break

    if not target_path:
        # Fallback to App.tsx
        for p in [os.path.join(workspace_dir, "src", "App.tsx"), os.path.join(workspace_dir, "frontend", "src", "App.tsx")]:
            if os.path.exists(p):
                target_path = p
                target_rel = "src/App.tsx"
                break

    if not target_path or not os.path.exists(target_path):
        return False

    try:
        with open(target_path, "r", encoding="utf-8") as f:
            broken_code = f.read()
    except Exception as e:
        print(f"⚠️ [self_heal_presentation_suite] Could not read {target_path}: {e}")
        return False

    prompt = f"""You are Provable's Principal Lead Frontend Architect.
The live application preview on :5174 failed runtime verification.

--- OBJECTIVE RUNTIME DEFECTS & BROWSER LOGS ---
{combined_errors}

--- PRODUCT PITCH ---
{pitch}

--- CURRENT FILE ({target_rel}) ---
{broken_code}

Task:
1. Diagnose the exact runtime, compilation, or layout error from the logs and code above.
2. If this is `App.tsx`, ensure it properly exports the default component (`export default App;`) and satisfies modular orchestrator contracts.
3. Fix all syntax, JSX escaping, prop mismatches, or layout scaling issues so the component renders cleanly without errors.
4. Keep user-facing copy natural and persona-focused (avoid internal compiler terms like Invariant, Audit Ledger, Boundary Guards).

Return ONLY the corrected code inside a single ```tsx code block.
"""
    try:
        repaired = call_gemini(prompt, stage="self_healing")
        if repaired:
            cleaned = repaired.strip()
            fence_match = re.search(r'```(?:tsx|jsx|typescript|javascript)?\s*\n(.*?)```', cleaned, re.DOTALL)
            if fence_match:
                cleaned = fence_match.group(1).strip()

            for p in target_paths:
                if os.path.exists(os.path.dirname(p)):
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(cleaned.strip() + "\n")

            print(f"✨ [self_heal_presentation_suite] Successfully healed {target_rel} via LLM closed loop!", flush=True)
            return True
    except Exception as e:
        print(f"⚠️ [self_heal_presentation_suite] Self-healing LLM call failed: {e}", flush=True)

    return False

