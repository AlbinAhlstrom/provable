"""The QA audit uses the page, not only measures it: it fills each form, submits it and reads what the API answered.

These tests drive a real headless browser against a small local server, because what is under test is the script that
runs in the page. They are skipped where no browser can start.
"""
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from onboarding.qa_form_check import FormCheck, exercise_forms, verdict_from_outcomes

pytestmark = pytest.mark.slow

PAGE = """<!doctype html><html><body>
<h1>Ask for care</h1>
<form id="inquiry">
  <input name="parent_name" required minlength="3">
  <input name="email" type="email" required>
  <input name="children" type="number" min="2" required>
  <input name="day" type="date" required>
  <select name="tier" required><option value="">Pick one</option><option value="evening">Evening</option></select>
  <input name="ages" required placeholder="e.g. 2, 5">
  <textarea name="notes"></textarea>
  <label><input name="agree" type="checkbox" required> I agree</label>
  %(extra)s
  <button type="submit">Send inquiry</button>
</form>
<script>
document.getElementById('inquiry').addEventListener('submit', function (event) {
  event.preventDefault();
  var data = Object.fromEntries(new FormData(event.target).entries());
  fetch('/api/inquiries', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data)});
});
</script></body></html>"""


class _Site:
    """A page with one form and an API whose answer to a create the test chooses."""

    def __init__(self, create_status: int, create_body: dict, extra: str = ""):
        self.requests = []
        site = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _answer(self, status, body, content_type="application/json"):
                payload = body if isinstance(body, bytes) else json.dumps(body).encode()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def do_GET(self):
                self._answer(200, (PAGE % {"extra": extra}).encode(), "text/html")

            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length") or 0)).decode()
                site.requests.append(("POST", self.path, json.loads(body or "{}")))
                self._answer(create_status, create_body)

            def do_DELETE(self):
                site.requests.append(("DELETE", self.path, None))
                self.send_response(204)
                self.send_header("Content-Length", "0")
                self.end_headers()

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}/"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture(scope="module")
def browser():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        options = Options()
        for arg in ("--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"):
            options.add_argument(arg)
        driver = webdriver.Chrome(options=options)
    except Exception as err:
        pytest.skip(f"no headless browser here: {err}")
    yield driver
    driver.quit()


def _check(browser, site) -> FormCheck:
    try:
        browser.get(site.url)
        return exercise_forms(browser, "Desktop")
    finally:
        site.close()


def test_a_form_the_api_accepts_passes_and_its_test_record_is_removed(browser):
    """Verify a working form is filled with values its fields accept, submitted, and cleaned up after.

    id: TST-QA-FORM-001
    Given: A page whose form posts to an API that answers 201 with the new record's id
    When: The form check runs
    Then: There is no defect, the API received a value for every required field, and the record was deleted again
    """
    site = _Site(201, {"id": "abc123", "notes": "n" * 900})  # a long answer: the id is read from all of it
    check = _check(browser, site)

    assert check.defects == [] and check.warnings == []
    (_, path, sent), (method, deleted_path, _) = site.requests
    assert path == "/api/inquiries"
    assert len(sent["parent_name"]) >= 3 and "@" in sent["email"] and int(sent["children"]) >= 2
    assert sent["day"] and sent["tier"] == "evening" and sent["agree"] == "on"
    assert sent["ages"] == "2, 5"  # a field's own example is the value it is given
    assert (method, deleted_path) == ("DELETE", "/api/inquiries/abc123")


def test_a_form_the_api_rejects_is_a_defect_that_quotes_the_answer(browser):
    """Verify a form whose submission the API refuses fails the audit with the API's own reason.

    id: TST-QA-FORM-002
    Given: A page whose form posts to an API that answers 422 naming the missing field
    When: The form check runs
    Then: One defect names the form, the request, the status and what the API said
    """
    site = _Site(422, {"detail": [{"loc": ["body", "created_at"], "msg": "Field required"}]})
    check = _check(browser, site)

    assert len(check.defects) == 1
    defect = check.defects[0]
    assert "[Desktop]" in defect and "Send inquiry" in defect and "POST /api/inquiries" in defect
    assert "422" in defect and "created_at" in defect
    assert [r[0] for r in site.requests] == ["POST"]  # nothing to remove


def test_a_form_the_check_cannot_fill_is_a_warning_not_a_defect(browser):
    """Verify the check says so when it could not complete a form, and blames nothing on the page.

    id: TST-QA-FORM-003
    Given: A form with a required field whose pattern the check cannot know how to satisfy
    When: The form check runs
    Then: A warning names the field, nothing was submitted and there is no defect
    """
    site = _Site(201, {"id": "x"}, extra='<input name="membership_code" required pattern="[A-Z]{3}-[0-9]{4}">')
    check = _check(browser, site)

    assert check.defects == []
    assert len(check.warnings) == 1 and "membership_code" in check.warnings[0]
    assert site.requests == []


def test_outcomes_become_defects_only_when_a_request_failed():
    """Verify the verdict rule in isolation: a refused or failed request is a defect, everything else a warning.

    id: TST-QA-FORM-004
    Given: Outcomes for a refused form, an unreachable API, a form that sent nothing and a record left behind
    When: They are turned into a verdict
    Then: The refused and the unreachable ones are defects, the other two are warnings
    """
    check = verdict_from_outcomes("Desktop", [
        {"label": "Book", "outcome": "submitted", "calls": [{"method": "POST", "url": "http://h/api/a", "status": 500, "body": "boom", "error": ""}]},
        {"label": "Ask", "outcome": "submitted", "calls": [{"method": "POST", "url": "http://h/api/b", "status": None, "body": "", "error": "TypeError: Failed to fetch"}]},
        {"label": "Next", "outcome": "no_request", "calls": []},
        {"label": "Join", "outcome": "submitted", "cleanup": "not_removed",
         "calls": [{"method": "POST", "url": "http://h/api/c", "status": 201, "body": "{}", "error": ""}]},
    ])
    assert len(check.defects) == 2
    assert "POST /api/a answered 500: boom" in check.defects[0] and "Failed to fetch" in check.defects[1]
    assert len(check.warnings) == 2 and "Next" in check.warnings[0] and "Join" in check.warnings[1]
