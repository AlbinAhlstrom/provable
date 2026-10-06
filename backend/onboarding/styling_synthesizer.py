"""
Aesthetic Styling Pass — Step 5c of the Deterministic Compiler Graph.
Applies domain-native Tailwind CSS styling, color palettes, and visual polish
to working functional React components according to the pitch's intended audience.
"""

import os
import re
import time
from typing import List, Dict, Any, Optional
from agent_orchestrator import call_gemini
from onboarding.code_verifier import verify_tsx_syntax


def _extract_tsx_code(raw_response: str) -> Optional[str]:
    text = raw_response.strip()
    if "```tsx" in text:
        return text.split("```tsx", 1)[1].split("```", 1)[0].strip()
    elif "```jsx" in text:
        return text.split("```jsx", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        return text.split("```", 1)[1].split("```", 1)[0].strip()
    return text if ("import React" in text or "export" in text) else None


def style_single_component(
    file_path: str,
    pitch_spec: str
) -> bool:
    """
    Applies visual styling to a single React TSX file in-place,
    preserving 100% of functional logic and React hooks.
    """
    if not os.path.exists(file_path):
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()

    file_name = os.path.basename(file_path)

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "styling_synthesis.md")
    if not os.path.exists(prompt_path):
        return False

    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    prompt = template.replace("{pitch_spec}", pitch_spec)
    prompt = prompt.replace("{file_name}", file_name)
    prompt = prompt.replace("{component_code}", original_code)

    try:
        raw_res = call_gemini(prompt, stage="aesthetic_styling")
        styled_code = _extract_tsx_code(raw_res or "")
        if styled_code and len(styled_code) > 50:
            is_valid, _ = verify_tsx_syntax(styled_code)
            if is_valid:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(styled_code + "\n")
                return True
    except Exception as e:
        print(f"[StylingPass] Notice while styling {file_name}: {e}")

    return False


def run_aesthetic_styling_pipeline(
    workspace_dir: str,
    pitch_spec: str,
    component_files: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Executes the isolated aesthetic styling pass across synthesized React components.
    """
    start_time = time.time()
    src_dir = os.path.join(workspace_dir, "src")
    if not os.path.exists(src_dir):
        return {"success": False, "styled_count": 0}

    raw_targets = component_files or []
    if not raw_targets:
        for root, _, files in os.walk(src_dir):
            for file in files:
                raw_targets.append(os.path.join(root, file))

    # Only style visual React TSX components (exclude client.ts, main.tsx, etc.)
    targets = [
        t for t in raw_targets
        if t.endswith(".tsx") and not t.endswith("main.tsx")
    ]

    styled_count = 0
    print(f"[Compiler:StylingPass] Applying domain-native styling in parallel to {len(targets)} UI components...", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=min(len(targets) or 1, 6)) as executor:
        future_map = {executor.submit(style_single_component, t, pitch_spec): t for t in targets}
        for fut in as_completed(future_map):
            t = future_map[fut]
            try:
                success = fut.result()
                if success:
                    styled_count += 1
                    print(f"[Compiler:StylingPass] ✓ Styled {os.path.basename(t)}", flush=True)
            except Exception as e:
                print(f"[Compiler:StylingPass] Notice for {os.path.basename(t)}: {e}")

    elapsed = round(time.time() - start_time, 2)
    print(f"[Compiler:StylingPass] Completed in {elapsed}s ({styled_count}/{len(targets)} components enhanced).", flush=True)
    return {
        "success": True,
        "styled_count": styled_count,
        "total_targets": len(targets),
        "elapsed_seconds": elapsed
    }
