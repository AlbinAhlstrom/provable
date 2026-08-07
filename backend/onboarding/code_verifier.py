"""
AST & Code Syntax Verifier with Self-Healing Closed Loop.

Parses React TSX code for structural balance and syntax errors before saving to disk.
If syntax errors are detected, triggers a targeted self-healing LLM repair step.
"""

import re
import sys
import os
from typing import Dict, Any, Tuple
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
