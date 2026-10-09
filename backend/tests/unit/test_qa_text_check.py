"""The QA text check: an escape the page shows letter by letter is a defect the one rework is told about."""
from onboarding import qa_text_check as tc


def test_an_escape_shown_as_letters_is_a_defect_quoted_with_its_text():
    """Verify the rework is told which text carries an escape that was never read.

    id: TST-QA-TEXT-001
    Given: A heading that shows a symbol followed by the six letters of a Unicode escape, and an ordinary label
    When: The verdict is drawn
    Then: One defect: it names the device, the escape and the text it stands in, and says where an escape is read
    """
    check = tc.verdict_from_texts("Desktop", ["★\\uFE0E Favourites", "Save"])
    assert len(check.defects) == 1
    defect = check.defects[0]
    assert defect.startswith("[Desktop]") and "\\uFE0E" in defect and '"★\\uFE0E Favourites"' in defect
    assert "JavaScript string" in defect and "Save" not in defect


def test_an_entity_shown_as_letters_is_a_defect():
    """
    id: TST-QA-TEXT-002
    Given: A label that shows an HTML entity as written (named, and numbered)
    When: The verdict is drawn
    Then: Each is a defect naming the entity
    """
    check = tc.verdict_from_texts("Desktop", ["Terms&nbsp;of use", "Price &#8364;20"])
    assert len(check.defects) == 2
    assert "&nbsp;" in check.defects[0] and "&#8364;" in check.defects[1]


def test_ordinary_text_is_left_alone():
    """Verify the check only speaks of escapes: a path, an ampersand and a symbol are text like any other.

    id: TST-QA-TEXT-003
    Given: Text with backslashes, ampersands and symbols that is not an escape
    When: The verdict is drawn
    Then: No defect
    """
    check = tc.verdict_from_texts("Desktop", ["C:\\users\\name", "Salt & pepper; mild", "★ 4.5", "R&D; labs", "a\\b"])
    assert check.defects == []


def test_one_escape_is_reported_once_however_many_texts_show_it():
    """
    id: TST-QA-TEXT-004
    Given: Twelve texts showing the same escape and one showing another
    When: The verdict is drawn
    Then: Two defects, the escape touching more texts first, with how many and a few of them quoted
    """
    texts = [f"♦\\uFE0E {i}" for i in range(12)] + ["x\\u00e9"]
    check = tc.verdict_from_texts("Desktop", texts)
    assert len(check.defects) == 2
    assert "12 text(s)" in check.defects[0] and "\\uFE0E" in check.defects[0] and "\\u00e9" in check.defects[1]
    assert check.defects[0].count('"♦') == tc.SAMPLES_QUOTED


def test_a_check_that_could_not_run_is_a_warning():
    """
    id: TST-QA-TEXT-005
    Given: A browser that refuses the script
    When: The page's text is read
    Then: A warning, no defect
    """
    class Broken:
        def execute_script(self, script):
            raise RuntimeError("no page")

    check = tc.read_text(Broken(), "Desktop")
    assert check.defects == [] and "could not run" in check.warnings[0]


def test_the_text_is_read_from_the_page_the_browser_has_open():
    """
    id: TST-QA-TEXT-006
    Given: A browser whose page shows one text with an escape
    When: The page's text is read
    Then: The defect is drawn from what the browser returned
    """
    class Browser:
        def execute_script(self, script):
            return ["⚙\\uFE0E Loading"]

    assert len(tc.read_text(Browser(), "Desktop").defects) == 1
