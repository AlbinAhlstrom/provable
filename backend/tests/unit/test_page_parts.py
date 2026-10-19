"""The parts of a page: named once by the plan, listed to the page's writer, and looked for in what it wrote.

A page written without hidden thinking came back a fifth of its planned size: the grid and its header were there,
and a menu, a dialog and two effects the plan named were not. QA measures layout and forms, so it passed. The plan
already names every part by role and name; code reads that list out, the writer is shown it as the page's parts and
says where it writes each before the files, and the same list is what the written page is checked against.

A part's role and name were then copied from its line by the page's writer, and by a test's writer on the other
side. The page gave a field for a day the role of a date input, a choice the role of a list's item and a message no
name at all: each was there for a person, and none was found by the role and name of its line. So the line is
turned into code for the page as well (`src/api/parts.ts`): the writer spreads a part's call on its element, and
the call is what the page is looked through for.
"""
import json
import os
import subprocess

from onboarding import code_verifier
from onboarding.page_gates import run_page_gates
from onboarding.page_parts import (Part, field_wordings, locators_block, missing_parts, parts_block, parts_of,
                                   props_module, shown_values)
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

WHOLE = '''import { parts } from '../api/parts';
export const BasketView = () => (
  <main>
    <ul {...parts.basket()}>{lines.map(l => <li key={l.id} {...parts.line({ quantity: l.quantity, dish: l.dish })}>{l.dish}</li>)}</ul>
    <output {...parts.total({ amount })} />
    <button {...parts.order()} onClick={() => setAsking(true)}>Order</button>
    {asking && <div {...parts.addressDialog()}><input {...parts.street()} /></div>}
  </main>
);
'''
# The same page as a writer in a hurry leaves it: the button is there, what it opens is not
SHORT = '''import { parts } from '../api/parts';
export const BasketView = () => (
  <main>
    <ul {...parts.basket()}>{lines.map(l => <li key={l.id} {...parts.line({ quantity: l.quantity, dish: l.dish })}>{l.dish}</li>)}</ul>
    <output {...parts.total({ amount })} />
    <button {...parts.order()} onClick={place}>Order</button>
  </main>
);
'''
# The parts as a writer gives them a role and a name of its own: there for a person, found by no line of the plan
OWN = '''export const BasketView = () => (
  <main>
    <div role="list">{lines.map(l => <button key={l.id} role="listitem" aria-label={`${l.quantity} x ${l.dish}`} />)}</div>
    <p role="status">Total {amount}</p>
    <button onClick={() => setAsking(true)}>Order</button>
    {asking && <div role="dialog" aria-label="Delivery address"><input type="date" aria-label="Street" /></div>}
  </main>
);
'''
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
TYPESCRIPT = os.path.join(REPO, "frontend", "node_modules", "typescript", "lib", "typescript.js")
RUNNER = r"""
const ts = require(process.argv[1]);
const source = require('fs').readFileSync(0, 'utf8');
const compiled = ts.transpileModule(source, { compilerOptions: { module: 'commonjs', target: 'es2019' } }).outputText;
const mod = { exports: {} };
new Function('module', 'exports', compiled)(mod, mod.exports);
const parts = mod.exports.parts;
console.log(JSON.stringify({
  names: Object.keys(parts),
  order: parts.order(),
  line: parts.line({ quantity: 2, dish: 'soup' }),
  total: parts.total({ amount: '12.50' }),
}));
"""


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
    Given: A page that spreads the call of every part of the plan on an element
    When: It is checked against the plan's parts
    Then: Nothing is missing
    """
    assert missing_parts(parts_of(PLAN), [WHOLE]) == []


def test_a_part_given_a_role_and_a_name_by_hand_is_not_the_part_of_the_plan():
    """Verify the page is held to the call, not to something that looks like the part.

    id: TST-PARTS-010
    Given: A page that writes every part with a role and a name of its own and spreads no call
    When: It is checked against the plan's parts
    Then: Every part is missing, and each defect names the call to spread on the part's element
    """
    missing = missing_parts(parts_of(PLAN), [OWN])

    assert len(missing) == 6
    assert "{...parts.line({ quantity, dish })}" in missing[1] and "{...parts.addressDialog()}" in missing[3]


def test_a_call_gives_an_element_the_role_and_the_name_of_its_line():
    """
    id: TST-PARTS-011
    Given: The module written for the page from the plan
    When: It is run, and the calls of a part without values and of two parts with values are made
    Then: Each part has a call, and a call returns the role of its line and the name of its line with the values
          filled in, as the attributes an element is read out by
    """
    ran = subprocess.run(["node", "-e", RUNNER, TYPESCRIPT], input=props_module(parts_of(PLAN)),
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert ran.returncode == 0, ran.stderr
    seen = json.loads(ran.stdout)

    assert seen["names"] == ["basket", "line", "order", "addressDialog", "street", "total"]
    assert seen["order"] == {"role": "button", "aria-label": "Order"}
    assert seen["line"] == {"role": "listitem", "aria-label": "2 x soup"}
    assert seen["total"] == {"role": "status", "aria-label": "Total 12.50"}


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
    dialog = 'export const Ask = () => <dialog {...parts.addressDialog()}><textarea {...parts.street()} /></dialog>;'
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
    assert "{page_parts}" in prompt and "`src/api/parts.ts` exports exactly `parts`" in prompt
    synthesizer = open(os.path.join(os.path.dirname(code_verifier.__file__), "presentation_projection_synthesizer.py"),
                       encoding="utf-8").read()
    assert ("client_files[page_parts.FILE_NAME] = page_parts.props_module(planned, page_parts.field_wordings(ux_blueprint))"
            in synthesizer)
    form = prompt[prompt.rindex("Answer with"):]
    assert form.index("<<<parts>>>") < form.index(f"<<<{SECTIONS[0]}>>>") and form.rstrip().endswith("<<<end>>>")

    block = parts_block(PLAN)
    assert '- Address dialog · dialog · "Delivery address" · `{...parts.addressDialog()}`' in block and "(6)" in block
    assert '- Line · listitem · "{quantity} x {dish}" · `{...parts.line({ quantity, dish })}`' in block
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


def test_a_value_written_a_way_of_its_own_is_shown_beside_the_part_whose_name_it_fills():
    """Verify the page and the plan agree on a name built from a shown value: the writer handed a counter's bare
    number into its name while the plan writes that value with three digits, so the page read out "Mines left 10"
    where every rule expected the plan's "010". How the value is written stood in the wordings, far from the part.

    id: TST-PARTS-SHOWN-BESIDE
    Given: A plan whose part's name is built from a shown value with a written form of its own
    When: The page's writer is shown the parts
    Then: The value's definition stands right under that part's call, and not under a part that does not use it
    """
    block = parts_block(PLAN)
    lines = block.splitlines()
    total = next(i for i, line in enumerate(lines) if "parts.total(" in line)
    assert lines[total + 1].strip() == "`amount` is handed in as the person is shown it: the sum of the lines"
    assert block.count("the sum of the lines") == 1


WORDED = '''### 3. How each part is read out (role and name, used as written)
- Order state · status · "Order {status wording}"
- Send · button · "Send"

### 4. Wordings
- `Order.status` draft: not sent yet; shown as "Being written"
- `Order.status` sent: on its way; shown as "Sent"
'''


def test_a_fields_wording_is_put_into_the_name_by_the_call():
    """Verify a name built from a field's `shown as` wording gets that wording whoever writes the page: the writer
    handed a status's bare value into a button's name ("New game, lost") where every rule expected its wording
    ("New game, dead"), and in another run wrote the wording of a value nobody defined. The plan lists every wording,
    so the call is written from that list by code and is handed the value the record holds.

    id: TST-PARTS-FIELD-WORDING-CALL
    Given: A plan whose part's name holds `{status wording}`, and the wordings of `Order.status`
    When: The page's module is run and the part's call is made with each value of the field
    Then: The call takes `status` and the name holds that value's wording
    """
    runner = RUNNER.replace("""  order: parts.order(),
  line: parts.line({ quantity: 2, dish: 'soup' }),
  total: parts.total({ amount: '12.50' }),""", """  draft: parts.orderState({ status: 'draft' }),
  sent: parts.orderState({ status: 'sent' }),""")
    ran = subprocess.run(["node", "-e", runner, TYPESCRIPT], input=props_module(parts_of(WORDED), field_wordings(WORDED)),
                         capture_output=True, text=True, encoding="utf-8", timeout=60)
    assert ran.returncode == 0, ran.stderr
    seen = json.loads(ran.stdout)

    assert seen["draft"] == {"role": "status", "aria-label": "Order Being written"}
    assert seen["sent"] == {"role": "status", "aria-label": "Order Sent"}


def test_the_writers_hand_in_the_value_the_record_holds():
    """
    id: TST-PARTS-FIELD-WORDING-BESIDE
    Given: A plan whose part's name holds `{status wording}`, and the wordings of `Order.status`
    When: The page's writer and a page test's writer are shown the parts
    Then: The part's call takes `status`, and under it stands that it is the value `Order.status` holds, with the
          wording the call puts in for each, under no other part
    """
    for block in (parts_block(WORDED), locators_block(parts_of(WORDED), shown_values(WORDED), field_wordings(WORDED))):
        lines = block.splitlines()
        state = next(i for i, line in enumerate(lines) if "orderState" in line or "order_state" in line)
        assert "parts.orderState({ status })" in lines[state] or "parts.order_state(page, status=...)" in lines[state]
        assert lines[state + 1].strip() == ('`status` is handed in as `Order.status` holds it, and the call puts in its '
                                            'wording: draft "Being written", sent "Sent"')
        assert block.count("Being written") == 1


def test_a_wording_two_fields_give_differently_is_left_to_the_writer_with_both():
    """
    id: TST-PARTS-FIELD-WORDING-TWO
    Given: A part's `{status wording}`, where `Order.status` and `Table.status` word their values differently
    When: The writers are shown the parts
    Then: The call takes `status_wording` as written, and under it stand both fields' wordings
    """
    plan = WORDED + '- `Table.status` free: nobody sits there; shown as "Free"\n'
    assert field_wordings(plan) == {}
    block = parts_block(plan)
    assert "parts.orderState({ status_wording })" in block
    assert 'the wording of `Order.status`: draft "Being written", sent "Sent"; the wording of `Table.status`: free "Free"' in block


def test_the_writer_places_each_part_in_one_of_the_files_its_answer_has():
    """Verify the plan of the files names only files the answer can hold: a writer planned a menu in a component file
    of its own, imported it from the app and wrote no block for it, so the page failed to start, and the repair, which
    may change only files that exist, could not add it.

    id: TST-PARTS-ANSWER-FILES
    Given: The page prompt
    When: Its parts block is read
    Then: Each part is placed by the marker of one of the answer's files, every marker is named there, and these are
          said to be all the files the page has
    """
    path = os.path.join(os.path.dirname(code_verifier.__file__), "..", "prompts", "presentation_projection_synthesis.md")
    prompt = open(path, encoding="utf-8").read()
    form = prompt[prompt.rindex("<<<parts>>>"):]
    plan_line = form.splitlines()[1]
    assert "<the marker of the file you write it in" in plan_line
    assert all(section in plan_line for section in SECTIONS)
    assert "the only files of the page" in plan_line
