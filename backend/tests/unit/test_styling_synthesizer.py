"""
Hermetic offline unit tests for Styling Synthesizer (Step 5c).
Ensures zero hardcoded domain keywords and proper fallback on error.
"""

import os
from unittest.mock import patch
from onboarding.styling_synthesizer import run_aesthetic_styling_pipeline, style_single_component


def test_styling_synthesizer_has_zero_hardcoded_domain_keywords():
    style_py = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "onboarding", "styling_synthesizer.py"))
    with open(style_py, "r", encoding="utf-8") as f:
        code = f.read()

    forbidden = ["babysitter", "childcare", "chess", "minesweeper", "pizza", "flappy", "warehouse"]
    for word in forbidden:
        assert word not in code.lower(), f"Forbidden domain keyword '{word}' hardcoded in styling_synthesizer.py"


def test_styling_prompt_has_zero_hardcoded_domain_keywords():
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "styling_synthesis.md"))
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read()

    forbidden = ["babysitter", "childcare", "chess", "minesweeper", "pizza", "flappy", "warehouse"]
    for word in forbidden:
        assert word not in prompt_text.lower(), f"Forbidden domain keyword '{word}' hardcoded in styling_synthesis.md"


def test_styling_pipeline_preserves_on_failure(tmp_path):
    tsx_file = tmp_path / "App.tsx"
    original_code = "export default function App() { return <div>Original</div>; }"
    tsx_file.write_text(original_code, encoding="utf-8")

    with patch("onboarding.styling_synthesizer.call_gemini", side_effect=Exception("API error")):
        res = style_single_component(str(tsx_file), "Test pitch")
        assert res is False
        assert tsx_file.read_text(encoding="utf-8") == original_code
