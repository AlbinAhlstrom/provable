"""The parts of a page: named once by the plan, listed to the page's writer, and looked for in what it wrote.

A page written without hidden thinking came back a fifth of its planned size: the grid and its header were there,
and a menu, a dialog and two effects the plan named were not. QA measures layout and forms, so it passed. The plan
already names every part by role and name; code reads that list out, the writer is shown it as the page's parts and
says where it writes each before the files, and the same list is what the written page is checked against.
"""
import os

from onboarding import code_verifier
from onboarding.page_gates import run_page_gates
from onboarding.page_parts import Part, missing_parts, parts_block, parts_of
from onboarding.presentation_projection_synthesizer import SECTIONS, parse_file_blocks

PLAN = '''### 2. Where each action is done
- `place_order`: the "Order" button under the basket

### 3. How each part is read out (role and name, used as written)
- Basket · list · "Basket"
- Line · listitem · "{quantity} x {dish}"
- Order · button · "Order"
- Address dialog · dialog · "Delivery address"
- Street · textbox · "Street"
- Total · status · "Total {amount}"

### 4. Wordings
- shown value: amount = the sum of the lines
'''

WHOLE = '''export const BasketView = () => (
  <main>
    <ul aria-label="Basket">{lines.map(l => <li key={l.id}>{`${l.quantity} x ${l.dish}`}</li>)}</ul>
    <output aria-label={`Total ${amount}`} />
    <button onClick={() => setAsking(true)}>Order</button>
    {asking && <div role="dialog" aria-label="Delivery address"><input aria-label="Street" /></div>}
  </main>
);
'''
# The same page as a writer in a hurry leaves it: the button is there, what it opens is not
SHORT = '''export const BasketView = () => (
  <main>
    <ul aria-label="Basket">{lines.map(l => <li key={l.id}>{`${l.quantity} x ${l.dish}`}</li>)}</ul>
    <output aria-label={`Total ${amount}`} />
    <button onClick={place}>Order</button>
  </main>
);
'''


def test_the_parts_are_read_out_of_the_plan():
    """
    id: TST-PARTS-001
    Given: A page plan whose third section names each part by role and name, among other lists
    When: The parts are read out
    Then: They are those six, in the plan's order, and a plan that names none gives none
    """
    parts = parts_of(PLAN)
    assert [p.what for p in parts] == ["Basket", "Line", "Order", "Address dialog", "Street", "Total"]
    assert parts[3] == Part(what="Address dialog", role="dialog", name="Delivery address")
    assert parts_of("### 1. Opening\nA calm page.\n- `book`: the button") == []


def test_a_page_with_every_part_has_none_missing():
    """
    id: TST-PARTS-002
    Given: A page that writes every part of the plan, native elements for some roles and patterns filled in for names
    When: It is checked against the plan's parts
    Then: Nothing is missing
    """
    assert missing_parts(parts_of(PLAN), [WHOLE]) == []


def test_a_part_the_page_left_out_is_named_as_a_defect():
    """
    id: TST-PARTS-003
    Given: A page without the dialog the plan names, and so without the field inside it
    When: It is checked against the plan's parts
    Then: Each of the two is a defect that says what the part is, its role and the name it is read out by
    """
    missing = missing_parts(parts_of(PLAN), [SHORT])
    assert len(missing) == 2
    assert 'Address dialog' in missing[0] and 'dialog' in missing[0] and '"Delivery address"' in missing[0]
    assert '"Street"' in missing[1]
    assert all(defect.startswith("[Missing part] ") for defect in missing)


def test_a_part_spread_over_the_page_files_is_found():
    """
    id: TST-PARTS-004
    Given: A page whose dialog is written in a second file
    When: The files are checked together
    Then: Nothing is missing
    """
    dialog = 'export const Ask = () => <dialog aria-label="Delivery address"><textarea aria-label="Street" /></dialog>;'
    assert missing_parts(parts_of(PLAN), [SHORT, dialog]) == []


def test_the_writer_is_shown_the_parts_and_says_where_each_is_written_first():
    """
    id: TST-PARTS-005
    Given: The page prompt
    When: It is read
    Then: It has a place for the page's parts, and its answer opens with a parts block before the first file and
          still closes with the end marker
    """
    path = os.path.join(os.path.dirname(code_verifier.__file__), "..", "prompts", "presentation_projection_synthesis.md")
    prompt = open(path, encoding="utf-8").read()
    assert "{page_parts}" in prompt
    form = prompt[prompt.rindex("Answer with"):]
    assert form.index("<<<parts>>>") < form.index(f"<<<{SECTIONS[0]}>>>") and form.rstrip().endswith("<<<end>>>")

    block = parts_block(PLAN)
    assert '- Address dialog · dialog · "Delivery address"' in block and "(6)" in block
    assert "names no parts" in parts_block("### 1. Opening\nA calm page.")


def test_the_parts_block_of_an_answer_is_no_file():
    """
    id: TST-PARTS-006
    Given: An answer that opens with its parts block and then writes two files
    When: It is parsed
    Then: The files are the two files
    """
    answer = ("<<<parts>>>\nOrder -> view, places the order\n<<<view_tsx>>>\nexport const V = 1\n"
              "<<<app_tsx>>>\nexport const App = 1\n<<<end>>>\n")
    assert parse_file_blocks(answer) == {"view_tsx": "export const V = 1", "app_tsx": "export const App = 1"}


def _page(tmp_path, code):
    path = tmp_path / "src" / "views" / "BasketView.tsx"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(code, encoding="utf-8")
    return str(path)


def test_a_missing_part_goes_through_the_one_rework_qa_allows(tmp_path):
    """
    id: TST-PARTS-007
    Given: A page that measures clean in the browser and lacks two parts of its plan, and a rework that writes them
    When: The gates run
    Then: The rework is handed the two missing parts once, the page is measured again and passes after one rework
    """
    page = _page(tmp_path, SHORT)
    handed = []

    def rework(defects, console_errors):
        handed.append(defects)
        _page(tmp_path, WHOLE)
        return True

    outcome = run_page_gates(
        workspace_dir=str(tmp_path), pitch="p", presentation={"files": [page]}, ux_blueprint=PLAN,
        audit=lambda: {"passed": True, "defects": [], "console_errors": []}, rework=rework,
        review=lambda **kw: {"verdict": "fine", "problems": [], "edits": [], "not_repaired": [], "claims": [],
                             "attempts": 1, "error": None})

    assert len(handed) == 1 and len(handed[0]) == 2 and "Address dialog" in handed[0][0]
    assert outcome.qa["passed"] and outcome.qa["attempts"] == 1 and outcome.failures == []


def test_a_part_still_missing_after_the_rework_fails_qa(tmp_path):
    """
    id: TST-PARTS-008
    Given: A page that lacks parts of its plan, and a rework that leaves it as it was
    When: The gates run
    Then: QA reports the missing parts as defects that remain, after one rework and no more
    """
    page = _page(tmp_path, SHORT)
    calls = []
    outcome = run_page_gates(
        workspace_dir=str(tmp_path), pitch="p", presentation={"files": [page]}, ux_blueprint=PLAN,
        audit=lambda: {"passed": True, "defects": [], "console_errors": []},
        rework=lambda defects, errors: calls.append(1) or True)

    assert len(calls) == 1 and outcome.qa["verdict"] == "defects_remain"
    assert any("Address dialog" in defect for defect in outcome.qa["defects"])


def test_the_rework_is_shown_the_plan_a_missing_part_comes_from(tmp_path, monkeypatch):
    """
    id: TST-PARTS-009
    Given: A defect that names a missing part, and the page's plan
    When: The rework is asked for a fix
    Then: Its prompt carries the plan, so the part is written as planned and not guessed from its name
    """
    page = _page(tmp_path, SHORT)
    seen = {}

    def fake(prompt, stage="general", json_mode=False, **kw):
        seen["prompt"] = prompt
        return "<<<src/views/BasketView.tsx>>>\n" + WHOLE + "<<<end>>>\n"
    monkeypatch.setattr(code_verifier, "call_gemini", fake)

    healed = code_verifier.self_heal_presentation_suite(
        workspace_dir=str(tmp_path), pitch="p", defects=missing_parts(parts_of(PLAN), [SHORT]), console_errors=[],
        component_files=[page], plan=PLAN, compile_check=lambda ws, code: (True, ""))

    assert healed and "### 3. How each part is read out" in seen["prompt"] and "[Missing part]" in seen["prompt"]
