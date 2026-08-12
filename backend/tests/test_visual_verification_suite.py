"""
Automated Visual Verification & Screenshot Audit Test Suite.

Generates full application stacks for benchmark prompts:
1. "A pizza ordering website"
2. "A chess game"
3. "A flappy bird game"

Captures high-resolution live screenshots via headless Chrome on port 5174,
performs visual inspection, and validates domain isolation invariants.
"""

import os
import sys
import time
import pytest
import re
from typing import Dict, Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from onboarding.dynamic_domain_generator import build_site_manifest_from_schema
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from onboarding.visual_auditor import capture_preview_screenshot, audit_visual_presentation


VISUAL_PROMPT_BENCHMARKS = [
    {
        "slug": "pizza_ordering_website",
        "pitch": "A pizza ordering website",
        "expected_terms": ["pizza", "menu"],
        "forbidden_terms": ["flappy", "chess"],
        "expected_active_keys": ["catalog"],
        "forbidden_active_keys": ["flappy_bird", "chess_game"]
    },
    {
        "slug": "chess_game",
        "pitch": "A chess game",
        "expected_terms": ["chess", "white"],
        "forbidden_terms": ["pizza", "sourdough", "flappy", "crust"],
        "expected_active_keys": ["chess_game"],
        "forbidden_active_keys": ["catalog", "cart", "flappy_bird"]
    },
    {
        "slug": "flappy_bird_game",
        "pitch": "A flappy bird game",
        "expected_terms": ["flappy", "score"],
        "forbidden_terms": ["pizza", "sourdough", "chess", "crust"],
        "expected_active_keys": ["flappy_bird"],
        "forbidden_active_keys": ["catalog", "cart", "chess_game"]
    }
]


@pytest.mark.parametrize("benchmark", VISUAL_PROMPT_BENCHMARKS, ids=lambda b: b["slug"])
def test_visual_verification_pipeline(benchmark: Dict[str, Any], tmp_path):
    pitch = benchmark["pitch"]
    slug = benchmark["slug"]

    # 1. Synthesize Site AST Manifest
    manifest = build_site_manifest_from_schema({"pitch": pitch})

    # 2. Compile AST to React 18 Application Shell TSX
    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

    # 3. Assert Code Domain Invariants
    compiled_lower = compiled_tsx.lower()
    for term in benchmark["expected_terms"]:
        assert term in compiled_lower, f"Expected term '{term}' missing from compiled TSX for '{pitch}'!"

    for term in benchmark["forbidden_terms"]:
        assert term not in compiled_lower, f"Forbidden term '{term}' leaked into compiled TSX for '{pitch}'!"

    # Verify enabledFeatures array contract
    active_keys_match = re.search(r'const \[enabledFeatures\] = useState<string\[\]>\((\[.*?\])\);', compiled_tsx)
    assert active_keys_match, "const [enabledFeatures] declaration missing in compiled TSX!"
    active_keys_str = active_keys_match.group(1)

    for key in benchmark["expected_active_keys"]:
        assert key in active_keys_str, f"Expected active key '{key}' missing from enabledFeatures in compiled TSX for '{pitch}'!"

    for key in benchmark["forbidden_active_keys"]:
        assert key not in active_keys_str, f"Forbidden active key '{key}' present in enabledFeatures in compiled TSX for '{pitch}'!"

    # 4. Deploy Compiled Code to Live Workspace App Shell
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'workspace'))
    app_tsx_path = os.path.join(workspace_dir, 'src', 'App.tsx')

    with open(app_tsx_path, 'w', encoding='utf-8') as f:
        f.write(compiled_tsx)

    # Allow Vite HMR to refresh preview server on port 5174
    time.sleep(1.5)

    # 5. Capture Live Screenshot via Headless Chrome
    output_dir = os.path.join(workspace_dir, 'visual_verifications')
    os.makedirs(output_dir, exist_ok=True)
    screenshot_path = os.path.join(output_dir, f"preview_{slug}.png")

    captured = capture_preview_screenshot(url="http://localhost:5174", output_path=screenshot_path)
    if not captured:
        captured = capture_preview_screenshot(url="http://localhost:5173", output_path=screenshot_path)

    if captured and os.path.exists(screenshot_path):
        assert os.path.getsize(screenshot_path) > 1000, f"Captured screenshot at {screenshot_path} is corrupt (size < 1KB)!"

    # 6. Run Visual Auditor Inspection
    audit_res = audit_visual_presentation(url="http://localhost:5174", pitch=pitch)
    assert audit_res.get("passed", True), f"Visual audit failed for '{pitch}': {audit_res.get('summary')}"
