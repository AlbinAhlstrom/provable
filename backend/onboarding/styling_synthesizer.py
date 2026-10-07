"""
Aesthetic Styling Pass — Step 5c of the Deterministic Compiler Graph.
Applies domain-native Tailwind CSS styling, color palettes, and visual polish
to working functional React components according to the pitch's intended audience.

It restyles what the presentation stage delivered: the words the visitor reads and the component's logic are the
presentation stage's, and each restyle reports how far it moved from them (StyleResult).
"""

import pipeline_trace
from pipeline_trace import traced
import os
import re
import time
from dataclasses import asdict, dataclass, field
from typing import List, Dict, Any, Optional
from agent_orchestrator import call_gemini
from onboarding.verification import compile_tsx


@dataclass(frozen=True)
class StyleResult:
    """What restyling one component did. `reason` says why it was left as it was; it is empty when it was restyled."""
    path: str
    styled: bool
    reason: str = ""
    lines_before: int = 0
    lines_after: int = 0
    text_added: List[str] = field(default_factory=list)    # visitor-facing text only the restyled file has
    text_removed: List[str] = field(default_factory=list)  # visitor-facing text the restyle dropped
    attempts: int = 0                                      # LLM calls made: 2 means the first restyle was refused
    refusals: List[str] = field(default_factory=list)      # the verifier's verdict on each refused attempt


def _extract_tsx_code(raw_response: str) -> Optional[str]:
    text = raw_response.strip()
    if "```tsx" in text:
        return text.split("```tsx", 1)[1].split("```", 1)[0].strip()
    elif "```jsx" in text:
        return text.split("```jsx", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        return text.split("```", 1)[1].split("```", 1)[0].strip()
    return text if ("import React" in text or "export" in text) else None


_JSX_TEXT = re.compile(r">([^<>{}]*[A-Za-z][^<>{}]*)<")
_TEXT_ATTRIBUTE = re.compile(r"""\b(?:placeholder|title|alt|aria-label)=["']([^"']*[A-Za-z][^"']*)["']""")


def visible_text(code: str) -> List[str]:
    """The literal text a component shows: JSX text nodes and placeholder/title/alt/aria-label values. A measurement
    for the styling report (approximate: text built in expressions is not seen), never used to alter code."""
    found = {" ".join(t.split()) for t in _JSX_TEXT.findall(code) if ";" not in t and "=" not in t}
    found |= {" ".join(t.split()) for t in _TEXT_ATTRIBUTE.findall(code)}
    return sorted(t[:120] for t in found if t)


MAX_ATTEMPTS = 2  # first attempt + one retry fed the verifier's verdict (.claude/rules/pipeline.md, retry policy)


_EXPORT = re.compile(r"\bexport\s+(default\b|(?:const|function|class|let|var)\s+(\w+))")


def exported_names(code: str) -> set:
    """What a module exports: its named bindings, and "default" when it has a default export."""
    return {name or "default" for _, name in _EXPORT.findall(code)}


def _verify(original_code: str, styled_code: str, workspace_dir: str) -> str:
    """The reason a restyle is refused, or "" when it may replace the component. The restyle must still export what
    the other files import, and it must compile in the workspace the way the preview will compile it."""
    missing = sorted(exported_names(original_code) - exported_names(styled_code))
    if missing:
        return f"the restyled code no longer has the export(s) {', '.join(missing)} that other files import"
    compiles, verdict = compile_tsx(workspace_dir, styled_code)
    if not compiles:
        return f"the restyled code does not compile: {verdict}"
    return ""


@traced("styling.component")
def style_single_component(
    file_path: str,
    pitch_spec: str,
    workspace_dir: str
) -> StyleResult:
    """
    Applies visual styling to a single React TSX file in-place,
    preserving 100% of functional logic and React hooks.

    A restyle replaces the working component only once the verifier accepts it. A refusal is fed back for one more
    attempt; if that is refused too, the component stays as the presentation stage wrote it. Provider errors and
    answers without a component are never retried.
    """
    if not os.path.exists(file_path):
        return StyleResult(path=file_path, styled=False, reason="the file does not exist")

    with open(file_path, "r", encoding="utf-8") as f:
        original_code = f.read()
    lines_before = len(original_code.splitlines())
    attempts = 0
    refusals: List[str] = []

    def left_as_is(reason: str) -> StyleResult:
        return StyleResult(path=file_path, styled=False, reason=reason, lines_before=lines_before,
                           lines_after=lines_before, attempts=attempts, refusals=refusals)

    file_name = os.path.basename(file_path)

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "styling_synthesis.md")
    if not os.path.exists(prompt_path):
        return left_as_is("the styling prompt is missing")

    with open(prompt_path, "r", encoding="utf-8") as f:
        template = f.read()

    refusal = ""
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        feedback = (f"## Your previous restyle of this file was refused\n```\n{refusal}\n```\n"
                    "Restyle the component again and return the complete file with this fixed.\n\n") if refusal else ""
        prompt = template.replace("{pitch_spec}", pitch_spec)
        prompt = prompt.replace("{file_name}", file_name)
        prompt = prompt.replace("{feedback_block}", feedback)
        prompt = prompt.replace("{component_code}", original_code)

        try:
            raw_res = call_gemini(prompt, stage="aesthetic_styling")
        except Exception as e:
            print(f"[StylingPass] Notice while styling {file_name}: {e}")
            return left_as_is(f"{type(e).__name__}: {e}")
        if not raw_res:
            import agent_orchestrator
            return left_as_is(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")

        styled_code = _extract_tsx_code(raw_res)
        if not styled_code or len(styled_code) <= 50:
            return left_as_is("the answer contained no TSX component")
        refusal = _verify(original_code, styled_code, workspace_dir)
        if refusal:
            refusals.append(refusal)
            print(f"[StylingPass] Restyle of {file_name} refused (attempt {attempts}): {refusal}", flush=True)
            continue

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(styled_code + "\n")
        before, after = set(visible_text(original_code)), set(visible_text(styled_code))
        return StyleResult(path=file_path, styled=True, lines_before=lines_before, lines_after=len(styled_code.splitlines()),
                           text_added=sorted(after - before), text_removed=sorted(before - after), attempts=attempts,
                           refusals=refusals)
    return left_as_is(refusal)


@traced("styling.pass")
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

    # Styling restyles exactly the components the presentation stage delivered; with none, there is nothing to style
    # (never "everything under src/", which would hide that the presentation stage delivered nothing).
    raw_targets = list(component_files or [])
    if not raw_targets:
        return {"success": False, "styled_count": 0, "error": "no components were delivered to style"}

    # Only style the served app's visual React TSX components (exclude client.ts, main.tsx, etc.). The presentation stage
    # also mirrors its files into frontend/src, which nothing serves: styling those copies doubled the LLM cost.
    src_root = os.path.abspath(src_dir) + os.sep
    targets = [
        t for t in raw_targets
        if t.endswith(".tsx") and not t.endswith("main.tsx") and os.path.abspath(t).startswith(src_root)
    ]

    results: List[StyleResult] = []
    print(f"[Compiler:StylingPass] Applying domain-native styling in parallel to {len(targets)} UI components...", flush=True)

    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=min(len(targets) or 1, 6)) as executor:
        future_map = {executor.submit(pipeline_trace.bind_context(style_single_component), t, pitch_spec, workspace_dir): t
                      for t in targets}
        for fut in as_completed(future_map):
            t = future_map[fut]
            try:
                result = fut.result()
            except Exception as e:
                result = StyleResult(path=t, styled=False, reason=f"{type(e).__name__}: {e}")
            results.append(result)
            if result.styled:
                print(f"[Compiler:StylingPass] ✓ Styled {os.path.basename(t)} ({result.lines_before} -> {result.lines_after} lines)", flush=True)
            else:
                print(f"[Compiler:StylingPass] ✗ Left {os.path.basename(t)} as it was: {result.reason}", flush=True)

    styled_count = sum(1 for r in results if r.styled)
    elapsed = round(time.time() - start_time, 2)
    print(f"[Compiler:StylingPass] Completed in {elapsed}s ({styled_count}/{len(targets)} components enhanced).", flush=True)
    return {
        "success": True,
        "styled_count": styled_count,
        "total_targets": len(targets),
        "elapsed_seconds": elapsed,
        "results": sorted(
            ({**asdict(r), "file": os.path.relpath(r.path, workspace_dir).replace(os.sep, "/")} for r in results),
            key=lambda r: r["file"]),
    }
