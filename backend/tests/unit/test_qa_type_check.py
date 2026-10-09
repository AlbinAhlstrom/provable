"""The QA type check: a page that contradicts its own types is a defect the one rework is told about."""
import subprocess

from onboarding import qa_type_check as tc

OUTPUT = """src/views/MatchView.tsx(162,30): error TS2339: Property 'piece_type' does not exist on type '{ color?: string; type?: string; }'.
src/views/MatchView.tsx(165,34): error TS2339: Property 'piece_type' does not exist on type '{ color?: string; type?: string; }'.
src/views/MatchView.tsx(170,67): error TS2339: Property 'piece_color' does not exist on type '{ color?: string; type?: string; }'.
src/App.tsx(12,5): error TS2322: Type 'string' is not assignable to type 'number'.
"""


def _ran(returncode, stdout="", stderr=""):
    return lambda *args, **kwargs: subprocess.CompletedProcess(args, returncode, stdout=stdout, stderr=stderr)


def test_each_type_error_is_a_defect_naming_its_file_and_lines():
    """Verify the rework is told what the compiler said, once per cause.

    id: TST-QA-TYPES-001
    Given: The compiler's output with one message on two lines of a file, another message in it, and one in another file
    When: The defects are read from it
    Then: Three defects, each with its file, its line or lines and the compiler's own message
    """
    defects = tc.defects_from_output(OUTPUT)
    assert len(defects) == 3
    assert defects[0].startswith("[Types] src/views/MatchView.tsx lines 162, 165: Property 'piece_type' does not exist")
    assert "src/views/MatchView.tsx line 170: Property 'piece_color'" in defects[1]
    assert "src/App.tsx line 12: Type 'string' is not assignable to type 'number'." in defects[2]


def test_a_page_that_type_checks_has_no_defects(tmp_path):
    """Verify a clean check says nothing.

    id: TST-QA-TYPES-002
    Given: A compiler that exits cleanly
    When: The workspace is checked
    Then: No defects and no warnings
    """
    check = tc.check_types(str(tmp_path), run=_ran(0))
    assert check.defects == [] and check.warnings == []


def test_type_errors_fail_the_check(tmp_path):
    """Verify the compiler's refusal reaches the verdict.

    id: TST-QA-TYPES-003
    Given: A compiler that exits with errors
    When: The workspace is checked
    Then: The errors are defects
    """
    check = tc.check_types(str(tmp_path), run=_ran(2, stdout=OUTPUT))
    assert len(check.defects) == 3 and check.warnings == []


def test_a_compiler_that_could_not_run_is_a_warning_not_a_defect(tmp_path):
    """Verify the check's own failure is not blamed on the page.

    id: TST-QA-TYPES-004
    Given: A compiler that cannot be started, and one that fails without naming any error in the sources
    When: The workspace is checked
    Then: Each gives one warning that says the check could not run, and no defect
    """
    def missing(*args, **kwargs):
        raise FileNotFoundError("npx")

    for run in (missing, _ran(1, stderr="npm ERR! could not determine executable to run")):
        check = tc.check_types(str(tmp_path), run=run)
        assert check.defects == [] and len(check.warnings) == 1 and "could not run" in check.warnings[0]
