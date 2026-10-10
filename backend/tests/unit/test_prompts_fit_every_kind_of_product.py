"""The prompts ask a product only for what a product of its kind has (vault: ADR-009, phase 0).

They were tuned on a page that presents someone's offer to visitors, and asked every product for that page's parts: a
headline in its own voice, a brand header, a footer, an invented feel. A grid game then came out with an invented look
and with text that had nothing to say ("Tactical Terminal", "Deterministic deduction").
"""

import os

PROMPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts"))


def _prompt(name: str) -> str:
    with open(os.path.join(PROMPTS, name), encoding="utf-8") as handle:
        return handle.read()


def _direction() -> str:
    plan = _prompt("ux_planning.md")
    return plan[plan.index("6. **Visual Direction"):plan.index("Respond STRICTLY")]


def test_a_product_known_by_sight_is_given_the_look_people_know():
    """Verify the plan invents a look only for a product that has none of its own.

    id: TST-KINDS-001
    Given: The prompts of the pitch expansion, the UX plan and the visual review
    When: They are read
    Then: A product people know by sight keeps the look they know it by, with its parts drawn as one unit, and the
          review compares the page with that look
    """
    direction = _direction()
    assert "the look they know" in direction
    assert "one unit" in direction, "a familiar thing whose parts belong together is not drawn as separate cards"
    assert "know by sight" in _prompt("prompt_expansion.md")
    assert "AESTHETIC TONE" not in _prompt("prompt_expansion.md"), "a mood is asked for only where there is no known look"
    assert "the look they know" in _prompt("visual_review.md")


def test_a_page_meant_to_be_used_opens_with_the_thing_itself():
    """Verify a headline and a primary action are asked of a page that persuades, not of every page.

    id: TST-KINDS-002
    Given: The prompts of the UX plan and the visual review
    When: They are read
    Then: The first screen of a page meant to be used is its main view, ready to use, and the review holds a page to
          the first screen its direction states
    """
    for body in (_direction(), _prompt("visual_review.md")):
        assert "meant to persuade" in body and "meant to be used" in body


def test_every_text_on_a_page_has_a_job():
    """Verify no prompt reserves a place that must then be filled with words.

    id: TST-KINDS-003
    Given: The prompts of the UX plan, the page and the visual review
    When: They are read
    Then: Wording is a name, a label, a state, an instruction, a message or a record's field; the page's shell has a
          footer only when there is something for it to carry; the review reports text that has no such job
    """
    page = _prompt("presentation_projection_synthesis.md")
    for body in (_prompt("ux_planning.md"), page, _prompt("visual_review.md")):
        assert "has a job" in body
    assert "the one footer" not in page and "brand header" not in page
    assert "when there is something for it to carry" in page


def test_a_product_keeps_the_name_its_pitch_gave_it():
    """Verify the product is not renamed on its way to the page's header.

    id: TST-KINDS-004
    Given: The prompts of the pitch expansion and the decomposition
    When: They are read
    Then: Both name the product as the pitch names it
    """
    assert "as the pitch names it" in _prompt("prompt_expansion.md")
    assert "as the pitch names it" in _prompt("router_decomposition.md")


def test_a_wide_view_scrolls_inside_its_own_container():
    """Verify a table, grid or timeline wider than a phone keeps its form.

    id: TST-KINDS-005
    Given: The page prompt
    When: Its viewport rules are read
    Then: The page never scrolls sideways, and a view wider than the screen scrolls inside its own container
    """
    page = _prompt("presentation_projection_synthesis.md")
    assert "inside its own container" in page and "overflow-x-auto" in page


def test_no_prompt_fixes_how_many_entities_or_records_a_product_has():
    """Verify the size of a product's model and content follows the product.

    id: TST-KINDS-006
    Given: The prompts of the pitch expansion, the decomposition and the seed data
    When: They are read
    Then: None of them gives a fixed count of entities or of records in a list
    """
    assert "2 to 4" not in _prompt("prompt_expansion.md")
    assert "2 to 4" not in _prompt("router_decomposition.md")
    assert "3 to 5" not in _prompt("seed_data.md")


def test_the_expansion_lists_what_is_seen_and_what_is_done_apart():
    """Verify the specification states the look and the use part by part, for readers who see nothing else.

    id: TST-KINDS-007
    Given: The prompt of the pitch expansion
    When: It is read
    Then: It says its readers see only the specification, and asks for the parts a person sees and the things a
          person can do as two lists under headings of their own (a list sharing a heading was left out)
    """
    expansion = _prompt("prompt_expansion.md")
    assert "read this specification and nothing else" in expansion
    assert "### 2. How it looks" in expansion and "### 3. How it is used" in expansion
    assert "one line for each part a person sees" in expansion
    assert "One line for each thing a person can do" in expansion


def test_the_plan_builds_on_the_specification_and_adds_no_words_to_a_product_that_needs_none():
    """Verify the plan decides what the specification left open (planning everything afresh, it gave a game a
    status line and hints it never had, and left colours to phrases).

    id: TST-KINDS-008
    Given: The prompt of the UX plan
    When: It is read
    Then: It says the page's writer reads the specification and the plan both, a signal without words is not said
          again in a sentence, the wording a person reads is listed apart from what only a screen reader speaks,
          published content is not only a business's, the layout line is the view as the page opens, and the
          length is set a line at a time
    """
    plan = _prompt("ux_planning.md")
    assert "reads the specification above and this blueprint, both" in plan
    assert "does not say again in a sentence" in plan
    assert "**Seen**" in plan and "**Spoken only**" in plan
    assert "the presets a tool offers" in plan
    assert "the page still reads it from them" in plan, "content the specification names is read from records too"
    assert "as they stand on the first visit" in plan and "`columns` is always a number" in plan
    assert "under 500 words" not in plan and "at most 25 words a line" in plan
