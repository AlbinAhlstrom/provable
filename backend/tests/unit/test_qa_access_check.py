"""The QA access check: an element a screen reader announces as nothing is a defect the one rework is told about."""
from onboarding import qa_access_check as ac


def test_each_kind_of_nameless_element_is_one_defect_with_its_advice():
    """Verify the rework is told what kind of element lacks a name and how to give it one.

    id: TST-QA-ACCESS-001
    Given: Two icon-only buttons, a field with no label and a picture with no alt
    When: The verdict is drawn
    Then: Three defects in a fixed order (controls, fields, images), each naming the device, the count and the fix
    """
    check = ac.verdict_from_elements("Desktop", [
        {"kind": "image", "where": "img.hero"},
        {"kind": "control", "where": "button.icon"}, {"kind": "control", "where": "a.close"},
        {"kind": "field", "where": "input#email"},
    ])
    assert len(check.defects) == 3
    assert check.defects[0].startswith("[Desktop]") and "2 button(s) or link(s)" in check.defects[0]
    assert "aria-label" in check.defects[0] and "`button.icon`" in check.defects[0]
    assert "htmlFor" in check.defects[1] and "input#email" in check.defects[1]
    assert "alt" in check.defects[2] and "img.hero" in check.defects[2]


def test_a_page_whose_elements_all_have_names_has_no_defect():
    """
    id: TST-QA-ACCESS-002
    Given: Nothing nameless found
    When: The verdict is drawn
    Then: No defect
    """
    assert ac.verdict_from_elements("Desktop", []).defects == []


def test_samples_are_capped_and_unknown_kinds_ignored():
    """
    id: TST-QA-ACCESS-003
    Given: Ten nameless buttons and an element of a kind the check does not know
    When: The verdict is drawn
    Then: One defect counting all ten, quoting only a few
    """
    elements = [{"kind": "control", "where": f"button.b{i}"} for i in range(10)] + [{"kind": "other", "where": "x"}]
    check = ac.verdict_from_elements("Desktop", elements)
    assert len(check.defects) == 1 and "10 button(s)" in check.defects[0]
    assert check.defects[0].count("`button.b") == ac.SAMPLES_QUOTED


def test_a_check_that_could_not_run_is_a_warning():
    """
    id: TST-QA-ACCESS-004
    Given: A browser that refuses the script
    When: The names are read
    Then: A warning, no defect
    """
    class Broken:
        def execute_script(self, script):
            raise RuntimeError("no page")

    check = ac.read_names(Broken(), "Desktop")
    assert check.defects == [] and "could not run" in check.warnings[0]


def test_the_names_are_read_from_the_page_the_browser_has_open():
    """
    id: TST-QA-ACCESS-005
    Given: A browser whose page holds one nameless button
    When: The names are read
    Then: The defect is drawn from what the browser returned
    """
    class Browser:
        def execute_script(self, script):
            return [{"kind": "control", "where": "button.x"}]

    assert len(ac.read_names(Browser(), "Desktop").defects) == 1
