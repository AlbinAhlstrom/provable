"""The page-test harness, driven for real: a small app (an API and a page) and a headless browser.

What is under test is the harness the engine writes into every generated app (tests/e2e/conftest.py): a test's
records are its own, the page talks to that test's API, and the run's report says how a test ended.
"""
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from onboarding.page_tests import run_test

pytestmark = pytest.mark.slow

API = '''from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
_notes = {}


class Note(BaseModel):
    id: str
    text: str
    done: bool = False


@app.get("/api/notes")
def list_notes():
    return list(_notes.values())


@app.post("/api/notes", status_code=201)
def create_note(note: Note):
    _notes[note.id] = note.model_dump()
    return _notes[note.id]


@app.get("/api/notes/{note_id}")
def get_note(note_id: str):
    return _notes[note_id]


@app.post("/api/notes/{note_id}/action")
def act(note_id: str, request: dict):
    if request["action_type"] != "finish":
        raise HTTPException(status_code=404, detail="Unknown action")
    _notes[note_id]["done"] = True
    return {"success": True, "state": _notes[note_id]}
'''

PAGE = b"""<!doctype html><html><body><h1>Notes</h1><ul id="notes"></ul>
<script>
function show() {
  fetch('/api/notes?order=newest').then(function (r) { return r.json(); }).then(function (notes) {
    var list = document.getElementById('notes');
    list.innerHTML = '';
    notes.forEach(function (note) {
      var item = document.createElement('li');
      item.textContent = note.text + (note.done ? ' (done)' : '');
      var button = document.createElement('button');
      button.textContent = 'Finish ' + note.text;
      button.onclick = function () {
        fetch('/api/notes/' + note.id + '/action', {method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({action_type: 'finish', params: {}})}).then(show);
      };
      item.appendChild(button);
      list.appendChild(item);
    });
  });
}
show();
window.addEventListener('pagehide', function () {
  fetch('/api/notes', {method: 'POST', keepalive: true, headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: 'left', text: 'The page was left'})});
});
</script></body></html>"""

FINISHING = '''from playwright.sync_api import expect


def test_a_finished_note_says_so(app):
    app.given("notes", id="n1", text="Water the plants")
    page = app.open()
    page.get_by_role("button", name="Finish Water the plants").click()
    expect(page.get_by_role("listitem")).to_contain_text("Water the plants (done)")
    assert app.record("notes", "n1")["done"] is True


def test_another_test_sees_none_of_those_records(app):
    assert app.records("notes") == []
    page = app.open(width=375, height=812)
    expect(page.get_by_role("listitem")).to_have_count(0)
    assert page.viewport_size == {"width": 375, "height": 812}
'''

LEAVING = '''import time

from playwright.sync_api import expect


def test_leaving_the_page_is_recorded(app):
    app.given("notes", id="n1", text="Water the plants")
    page = app.open()
    expect(page.get_by_role("listitem")).to_have_count(1)
    page.goto("about:blank")
    deadline = time.time() + 5
    while time.time() < deadline and len(app.records("notes")) < 2:
        time.sleep(0.1)
    assert [note["id"] for note in app.records("notes")] == ["n1", "left"]
'''


@pytest.fixture
def small_app(tmp_path):
    """A workspace holding the API, and a server for the page that has no API of its own."""
    os.makedirs(tmp_path / "src")
    (tmp_path / "src" / "__init__.py").write_text("")
    (tmp_path / "src" / "app.py").write_text(API)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            found = not self.path.startswith("/api/")  # the page's own server knows no record
            body = PAGE if found else b"[]"
            self.send_response(200 if found else 500)
            self.send_header("Content-Type", "text/html" if found else "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield str(tmp_path), f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def test_a_test_arranges_records_through_the_api_and_acts_on_the_page(small_app):
    """
    Given: An app whose page lists notes and finishes one at a click
    When: A test creates a note, clicks on the page and reads the record back; a second test expects no notes
    Then: The run passes: the page talked to the test's own API, and the second test started with nothing
    """
    workspace, page_url = small_app
    verdict = run_test(workspace, "SPEC-001", FINISHING, page_url)
    assert (verdict.status, verdict.reason) == ("pass", None), verdict.evidence


def test_what_the_page_does_not_show_is_a_fail(small_app):
    """
    Given: The same app
    When: A test expects wording the page never shows
    Then: The run fails, and the reason is the expectation that did not hold
    """
    workspace, page_url = small_app
    source = FINISHING.replace("(done)", "(archived)")
    verdict = run_test(workspace, "SPEC-001", source, page_url)
    assert verdict.status == "fail" and verdict.control_not_found is False
    assert "AssertionError" in verdict.reason and "archived" in verdict.evidence


def test_a_control_the_page_does_not_offer_is_marked_as_such(small_app):
    """
    Given: The same app
    When: A test clicks a button the page does not have
    Then: The run fails as a control that was not found
    """
    workspace, page_url = small_app
    source = FINISHING.replace('name="Finish Water the plants"', 'name="Archive"')
    verdict = run_test(workspace, "SPEC-001", source, page_url)
    assert (verdict.status, verdict.control_not_found) == ("fail", True), verdict.evidence


def test_a_given_the_api_refuses_is_broken(small_app):
    """
    Given: The same app
    When: A test arranges a record the API refuses
    Then: The run is broken and the reason carries the API's answer
    """
    workspace, page_url = small_app
    source = FINISHING.replace('id="n1", text="Water the plants"', 'id="n1"')
    verdict = run_test(workspace, "SPEC-001", source, page_url)
    assert verdict.status == "broken" and "422" in verdict.reason


def test_what_the_page_sends_as_it_is_left_reaches_the_tests_own_api(small_app):
    """
    Given: An app whose page tells its API when it is being left
    When: A test opens the page, leaves it and reads the records back
    Then: The run passes: a request sent while the page goes away reached this test's API like any other
    """
    workspace, page_url = small_app
    verdict = run_test(workspace, "SPEC-001", LEAVING, page_url)
    assert (verdict.status, verdict.reason) == ("pass", None), verdict.evidence


def test_a_failed_test_says_what_the_page_sent_and_what_the_app_holds(small_app):
    """
    Given: The same app
    When: A test clicks on the page and then expects wording the page never shows
    Then: The verdict carries what the page sent to the app, what the app answered, and the arranged records as
          the app held them when the test ended; a test that passes carries none of it
    """
    workspace, page_url = small_app
    failed = run_test(workspace, "SPEC-001", FINISHING.replace("(done)", "(archived)"), page_url)
    assert failed.status == "fail"
    assert "POST /api/notes/n1/action" in failed.seen and '"action_type": "finish"' in failed.seen
    assert "answered 200" in failed.seen
    assert 'notes: [{"id": "n1", "text": "Water the plants", "done": true}]' in failed.seen
    assert run_test(workspace, "SPEC-001", FINISHING, page_url).seen == ""
