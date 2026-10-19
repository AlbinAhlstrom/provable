"""The present moment of a generated app has one source, `src/domain/clock.py`, which every test can set.

A rule that depends on the time (what is due, how long something took) is decided by the plan, read by the class's
code from the clock, and arranged by every test by setting the clock, so all of them mean the same moment.
"""
import importlib
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from onboarding import skeleton_builder

PROMPTS = os.path.join(os.path.dirname(__file__), "..", "..", "prompts")


def _prompt(name: str) -> str:
    with open(os.path.join(PROMPTS, name), encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def generated(tmp_path, monkeypatch):
    """A workspace holding the generated clock, tests conftest and an app with no records of its own."""
    (tmp_path / "src" / "domain").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "domain" / "__init__.py").write_text("")
    (tmp_path / "src" / "domain" / "clock.py").write_text(skeleton_builder.CLOCK_MODULE, encoding="utf-8")
    (tmp_path / "src" / "app.py").write_text(skeleton_builder.generate_app_module([]), encoding="utf-8")
    (tmp_path / "tests" / "conftest.py").write_text(skeleton_builder.TESTS_CONFTEST, encoding="utf-8")
    monkeypatch.syspath_prepend(str(tmp_path))
    for name in [m for m in sys.modules if m == "src" or m.startswith("src.")]:
        monkeypatch.delitem(sys.modules, name)
    return tmp_path


def test_the_clock_reads_the_real_time_until_a_moment_is_set(generated):
    """
    id: TST-NOW-001
    Given: The clock the engine writes into every generated app
    When: Nothing sets it, then a moment is set as text, then it is let go
    Then: It reads the real time, then exactly that moment with its offset, then the real time again
    """
    from src.domain import clock

    before = datetime.now(timezone.utc)
    assert before <= clock.now() <= datetime.now(timezone.utc)
    clock.set_now("2030-01-31T09:30:10+00:00")
    assert clock.now() == datetime(2030, 1, 31, 9, 30, 10, tzinfo=timezone.utc)
    clock.set_now(None)
    assert clock.now().year == datetime.now(timezone.utc).year


def test_a_moment_one_unit_test_sets_is_gone_in_the_next(generated):
    """
    id: TST-NOW-002
    Given: Two unit tests in a generated app, the first of which sets the clock
    When: They run in order under the generated tests conftest
    Then: The second reads the real time
    """
    (generated / "tests" / "test_two.py").write_text(textwrap.dedent('''
        from datetime import datetime, timezone
        from src.domain import clock

        def test_a_sets_the_moment():
            clock.set_now("2030-01-31T09:30:00+00:00")
            assert clock.now().year == 2030

        def test_b_reads_the_real_time():
            assert clock.now().year == datetime.now(timezone.utc).year
    '''), encoding="utf-8")
    ran = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_two.py"],
                         cwd=generated, capture_output=True, text=True)
    assert ran.returncode == 0, ran.stdout + ran.stderr


def test_only_an_api_started_for_page_tests_lets_the_clock_be_set(generated, monkeypatch):
    """
    id: TST-NOW-003
    Given: The generated app's API
    When: It is started as the running app, and as a page test starts it
    Then: The running app offers no way to set its clock; the page test's API holds the moment it is sent
    """
    monkeypatch.delenv("APP_CLOCK_SETTABLE", raising=False)
    from src import app as running
    assert TestClient(running.app).put("/test/clock", json={"now": "2030-01-31T09:30:00+00:00"}).status_code in (404, 405)

    monkeypatch.setenv("APP_CLOCK_SETTABLE", "1")
    under_test = importlib.reload(running)
    from src.domain import clock
    answer = TestClient(under_test.app).put("/test/clock", json={"now": "2030-01-31T09:30:00+00:00"})
    assert answer.status_code == 200
    assert clock.now() == datetime(2030, 1, 31, 9, 30, tzinfo=timezone.utc)
    clock.set_now(None)


def test_the_scaffold_writes_the_clock_into_every_app():
    """
    id: TST-NOW-004
    Given: The skeleton the engine writes for a generated app
    When: Its files are listed
    Then: The domain holds the clock module
    """
    structure = skeleton_builder.DomainStructureSchema(domain_name="Notes")
    files = skeleton_builder.generate_fullstack_skeleton_files(structure, base_path="ws")
    assert files[os.path.join("ws", "src", "domain", "clock.py")] == skeleton_builder.CLOCK_MODULE


def test_every_stage_that_meets_the_present_moment_uses_the_one_clock():
    """
    id: TST-NOW-005
    Given: The prompts of the plan, the class's code, its first tests, its RED tests and its page tests
    When: They are read
    Then: The plan states the moment a situation happens at; the code reads it from the clock; every test sets it
    """
    contract = _prompt("product_contract.md")
    assert "the present moment" in contract and "now 2030-01-31T09:30:10+00:00" in contract
    assert "clock.now()" in _prompt("green_class_repair.md")
    for name in ("first_tests.md", "red_test_generation.md"):
        assert 'clock.set_now("' in _prompt(name), name
        assert "from src.domain import clock" in _prompt(name), name
    page = _prompt("page_test_generation.md")
    assert "app.at(moment)" in page and 'app.at("' in page
