"""
Hermetic offline unit tests for Styling Synthesizer (Step 5c).
Ensures zero hardcoded domain keywords and proper fallback on error.
"""

import os
from unittest.mock import patch
from onboarding.styling_synthesizer import StyleResult, run_aesthetic_styling_pipeline, style_single_component


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
        res = style_single_component(str(tsx_file), "Test pitch", str(tmp_path))
        assert res.styled is False and "API error" in res.reason
        assert tsx_file.read_text(encoding="utf-8") == original_code


def test_styling_pass_with_no_delivered_components_fails_instead_of_styling_everything(tmp_path):
    """Verify a failed presentation stage is not masked by restyling the skeleton.

    id: TST-STY-NODELIVERY
    Given: A workspace with a skeleton App.tsx and an empty component list
    When: The styling pass runs
    Then: It reports failure, calls no LLM and leaves App.tsx untouched
    """
    (tmp_path / "src").mkdir()
    app = tmp_path / "src" / "App.tsx"
    app.write_text("export default function App() { return null; }", encoding="utf-8")
    with patch("onboarding.styling_synthesizer.call_gemini") as llm:
        res = run_aesthetic_styling_pipeline(str(tmp_path), "pitch", component_files=[])
    assert res["success"] is False and res["styled_count"] == 0 and res["error"]
    llm.assert_not_called()
    assert app.read_text(encoding="utf-8") == "export default function App() { return null; }"


def test_styling_restyles_only_the_served_components_not_their_mirrors(tmp_path):
    """Verify files mirrored into frontend/src are not styled a second time.

    id: TST-STY-SERVED
    Given: The same component in src/ and in the unserved frontend/src mirror, plus a main.tsx and a client
    When: The styling pass runs on all of them
    Then: Only the src/ component is sent to the model
    """
    served = tmp_path / "src" / "App.tsx"
    mirror = tmp_path / "frontend" / "src" / "App.tsx"
    for f in (served, mirror, tmp_path / "src" / "main.tsx"):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text("export default function App() { return null; }", encoding="utf-8")
    styled = []
    with patch("onboarding.styling_synthesizer.style_single_component",
               lambda path, pitch, workspace_dir: styled.append(path) or StyleResult(path=path, styled=True)):
        res = run_aesthetic_styling_pipeline(
            str(tmp_path), "pitch",
            component_files=[str(served), str(mirror), str(tmp_path / "src" / "main.tsx"), str(tmp_path / "src" / "api" / "client.ts")])
    assert styled == [str(served)] and res["total_targets"] == 1


_COMPONENT = """import React from 'react';
export const Card = () => (
  <section className="p-2">
    <h2>Care Offerings</h2>
    <button onClick={() => null}>Request This Care</button>
  </section>
);
export default Card;
"""


def test_a_restyle_reports_what_it_changed(tmp_path):
    """Verify the styling stage states its effect on size and on the words the visitor reads.

    id: TST-STY-REPORT
    Given: A component, and a model answer that restyles it, rewrites one heading and adds a badge
    When: The component is styled
    Then: The result holds the line counts before and after and the text that appeared and disappeared
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    answer = "```tsx\n" + _COMPONENT.replace("Care Offerings", "Offerings & Rates").replace(
        "<button", "<span>100% Reliable</span>\n    <button") + "```"
    with patch("onboarding.styling_synthesizer.call_gemini", return_value=answer), \
            patch("onboarding.styling_synthesizer.compile_tsx", lambda ws, code: (True, "")):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert res.styled is True and res.reason == ""
    assert (res.lines_before, res.lines_after) == (8, 9)
    assert res.text_added == ["100% Reliable", "Offerings & Rates"] and res.text_removed == ["Care Offerings"]


def test_an_answer_that_is_not_a_component_is_refused_with_the_reason(tmp_path):
    """Verify a rejected restyle says why (the verifier's verdict used to be thrown away).

    id: TST-STY-REASON
    Given: A component and a model answer the compiler rejects
    When: The component is styled
    Then: The file is untouched and the result carries the compiler's reason, for each refused attempt
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    with patch("onboarding.styling_synthesizer.call_gemini", return_value="```tsx\nexport const Card = () => (<div>broken</div>;\nexport default Card;\n```"), \
            patch("onboarding.styling_synthesizer.compile_tsx", lambda ws, code: (False, 'Expected ")" but found ";" (line 1)')):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert res.styled is False and 'Expected ")"' in res.reason
    assert len(res.refusals) == 2 and all('Expected ")"' in r for r in res.refusals)
    assert tsx_file.read_text(encoding="utf-8") == _COMPONENT


def test_the_pass_reports_every_component_and_why_one_was_left_as_it_was(tmp_path):
    """Verify the stage result names each file and the reason for any that was not restyled ('3/4' said nothing).

    id: TST-STY-PERFILE
    Given: Two delivered components, one of which the model fails on
    When: The styling pass runs
    Then: The result lists both files with their outcome and the failure reason
    """
    good, bad = tmp_path / "src" / "App.tsx", tmp_path / "src" / "views" / "View.tsx"
    for f in (good, bad):
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(_COMPONENT, encoding="utf-8")

    def fake(path, pitch, workspace_dir):
        return StyleResult(path=path, styled=path == str(good), reason="" if path == str(good) else "RateLimitError: quota")

    with patch("onboarding.styling_synthesizer.style_single_component", fake):
        res = run_aesthetic_styling_pipeline(str(tmp_path), "pitch", component_files=[str(good), str(bad)])
    assert res["styled_count"] == 1 and res["total_targets"] == 2
    by_file = {r["file"]: r for r in res["results"]}
    assert by_file["src/App.tsx"]["styled"] is True
    assert by_file["src/views/View.tsx"]["styled"] is False and "quota" in by_file["src/views/View.tsx"]["reason"]


def test_the_styling_prompt_restyles_without_rewriting_the_copy():
    """Verify the prompt asks for a restyle of the existing elements and words, not for new content.

    id: TST-STY-PROMPT
    Given: The styling prompt
    When: It is read
    Then: It states that the visitor-facing text is kept verbatim and the file keeps its length
    """
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "styling_synthesis.md"))
    with open(prompt_path, "r", encoding="utf-8") as f:
        prompt_text = f.read().lower()
    assert "verbatim" in prompt_text and "same length" in prompt_text


def test_a_restyle_that_does_not_compile_is_retried_once_with_the_compiler_verdict(tmp_path):
    """Verify a restyle is proven by the workspace compiler before it replaces working code (a dropped `|` in a prop
    type passed the bracket check, crashed the preview and cost a 46 s QA repair).

    id: TST-STY-COMPILE
    Given: A first restyle the compiler rejects and a second one it accepts
    When: The component is styled with a workspace to compile in
    Then: The second prompt carries the compiler's verdict, the accepted restyle is written, and two attempts are reported
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    broken = _COMPONENT.replace("p-2", "p-4 broken")
    fixed = _COMPONENT.replace("p-2", "p-4")
    prompts = []

    def fake_llm(prompt, stage="general", **options):
        prompts.append(prompt)
        return "```tsx\n" + (broken if len(prompts) == 1 else fixed) + "```"

    def fake_compile(workspace_dir, code):
        return (False, 'Unexpected "null" (line 15)') if "broken" in code else (True, "")

    with patch("onboarding.styling_synthesizer.call_gemini", fake_llm), \
            patch("onboarding.styling_synthesizer.compile_tsx", fake_compile):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert res.styled is True and res.attempts == 2
    assert 'Unexpected "null" (line 15)' in prompts[1] and 'Unexpected "null"' not in prompts[0]
    assert tsx_file.read_text(encoding="utf-8").strip() == fixed.strip()


def test_a_restyle_that_never_compiles_leaves_the_working_component_in_place(tmp_path):
    """Verify the retry is bounded and the presentation stage's working file survives.

    id: TST-STY-COMPILE-KEEP
    Given: A model whose restyle fails to compile twice
    When: The component is styled
    Then: Exactly two calls are made, the file is unchanged, and the result carries the compiler's reason
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    calls = []

    def fake_llm(prompt, stage="general", **options):
        calls.append(prompt)
        return "```tsx\n" + _COMPONENT.replace("p-2", "p-4") + "```"

    with patch("onboarding.styling_synthesizer.call_gemini", fake_llm), \
            patch("onboarding.styling_synthesizer.compile_tsx", lambda ws, code: (False, "Expected identifier (line 3)")):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert len(calls) == 2 and res.styled is False and res.attempts == 2
    assert "does not compile" in res.reason and "Expected identifier" in res.reason
    assert tsx_file.read_text(encoding="utf-8") == _COMPONENT


def test_a_provider_error_is_not_retried(tmp_path):
    """Verify only a verifier's verdict earns the second attempt (retry policy).

    id: TST-STY-NORETRY
    Given: A model that returns nothing
    When: The component is styled
    Then: One call is made and the result says why
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    calls = []
    with patch("onboarding.styling_synthesizer.call_gemini", lambda prompt, stage="general", **o: calls.append(1) or ""):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert len(calls) == 1 and res.styled is False and res.reason


_NAMED_ONLY = """import React from 'react';
export const InquiryView: React.FC = () => (
  <section className="p-2">
    <h2>Offerings</h2>
  </section>
);
"""


def test_a_component_with_only_a_named_export_is_restyled(tmp_path):
    """Verify the verdict is the compiler's, not a guess about how a component must be exported (a rule that demanded
    `export default` or the word "App" refused two correct restyles in one run, and silently before that).

    id: TST-STY-NAMED
    Given: A view that exports only a named component, and a restyle that compiles and keeps that export
    When: The component is styled
    Then: The restyle is accepted on the first attempt
    """
    tsx_file = tmp_path / "InquiryView.tsx"
    tsx_file.write_text(_NAMED_ONLY, encoding="utf-8")
    answer = "```tsx\n" + _NAMED_ONLY.replace("p-2", "p-6 rounded-2xl") + "```"
    with patch("onboarding.styling_synthesizer.call_gemini", return_value=answer), \
            patch("onboarding.styling_synthesizer.compile_tsx", lambda ws, code: (True, "")):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert res.styled is True and res.attempts == 1 and res.refusals == []


def test_a_restyle_that_drops_an_export_is_refused_naming_it(tmp_path):
    """Verify a restyle cannot break the files that import the component.

    id: TST-STY-EXPORTS
    Given: A component exported by name and as default, and a restyle that compiles but lost the default export
    When: The component is styled
    Then: The restyle is refused, the reason names the missing export, and the file is unchanged
    """
    tsx_file = tmp_path / "Card.tsx"
    tsx_file.write_text(_COMPONENT, encoding="utf-8")
    answer = "```tsx\n" + _COMPONENT.replace("export default Card;", "") + "```"
    with patch("onboarding.styling_synthesizer.call_gemini", return_value=answer), \
            patch("onboarding.styling_synthesizer.compile_tsx", lambda ws, code: (True, "")):
        res = style_single_component(str(tsx_file), "pitch", str(tmp_path))
    assert res.styled is False and "default" in res.reason and "export" in res.reason
    assert tsx_file.read_text(encoding="utf-8") == _COMPONENT
