"""Unit tests for the page as a new visitor meets it (backend/onboarding/fresh_page.py): QA and the visual review look at
the page through an API started afresh, never at what the build or a person saved on the way."""

import contextlib
import json
import socket
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from onboarding import fresh_page, page_gates

APP = '''import os
from fastapi import FastAPI

app = FastAPI()


@app.get("/api/where")
def where():
    return {"data_dir": os.environ.get("APP_DATA_DIR", "unset")}
'''


def _workspace(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "src" / "app.py").write_text(APP, encoding="utf-8")
    return str(tmp_path)


@contextlib.contextmanager
def _page_server():
    """The running page: answers every request with the path it was asked for."""
    class Page(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            body = f"page {self.path}".encode()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Page)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()


@contextlib.contextmanager
def _socket_page():
    """A page server that switches every connection to a socket and echoes what it is sent, as the preview's
    reload socket does."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen()

    def serve():
        while True:
            try:
                conn, _ = listener.accept()
            except OSError:
                return
            with conn:
                asked = b""
                while b"\r\n\r\n" not in asked:
                    asked += conn.recv(1024)
                conn.sendall(b"HTTP/1.1 101 Switching Protocols\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
                data = conn.recv(1024)
                conn.sendall(data)

    threading.Thread(target=serve, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{listener.getsockname()[1]}"
    finally:
        listener.close()


def _get(url):
    with urllib.request.urlopen(url, timeout=10) as answer:
        return answer.read().decode()


@pytest.mark.slow  # starts the app's API
def test_the_page_is_reached_through_an_api_that_holds_nothing_saved(tmp_path):
    """Verify the page is judged as a new visitor meets it: a build once screenshotted a record an earlier class had
    saved (an empty board), and the review called a working page broken.

    id: TST-FRESH-PAGE-001
    Given: An app and its running page
    When: The page is opened through the fresh page's address
    Then: `/api/` is answered by an API that reads and saves nothing, everything else by the running page, and the
          API is gone once the page is closed
    """
    with _page_server() as page_url:
        with fresh_page.fresh_page(_workspace(tmp_path), page_url=page_url) as fresh:
            assert json.loads(_get(fresh.url + "/api/where")) == {"data_dir": ""}
            assert _get(fresh.url + "/src/main.tsx") == "page /src/main.tsx"
            assert _get(fresh.api_ready_url)  # the address QA waits on answers
            api = fresh.api_url
        with pytest.raises(OSError):
            _get(api + "/api/where")


@pytest.mark.slow  # starts the app's API
def test_the_page_keeps_its_reload_socket(tmp_path):
    """Verify a socket the page opens is carried through: the preview's reload socket refused at the door is logged
    by the browser as a severe error, which QA counts against the page.

    id: TST-FRESH-PAGE-002
    Given: A running page that switches a request to a socket
    When: The page asks for that socket through the fresh page's address
    Then: The switch and what is sent over the socket reach the page and come back
    """
    with _socket_page() as page_url:
        with fresh_page.fresh_page(_workspace(tmp_path), page_url=page_url) as fresh:
            port = int(fresh.url.rsplit(":", 1)[1])
            with socket.create_connection(("127.0.0.1", port), timeout=10) as conn:
                conn.sendall(b"GET /?token=t HTTP/1.1\r\nHost: x\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n")
                answer = b""
                while b"\r\n\r\n" not in answer:
                    answer += conn.recv(1024)
                assert answer.startswith(b"HTTP/1.1 101")
                conn.sendall(b"ping")
                assert conn.recv(1024) == b"ping"


def test_qa_and_the_visual_review_look_through_the_fresh_page(tmp_path, monkeypatch):
    """Verify both gates judge the page as a new visitor meets it, through one fresh API for the whole judgement.

    id: TST-FRESH-PAGE-003
    Given: The page gates with the real audit
    When: QA audits the page and the visual review audits it again
    Then: Each audit opens the fresh page's address and waits on its API, and the fresh page is opened once
    """
    from onboarding import qa_auditor
    audited, opened = [], []

    def audit(**kwargs):
        audited.append(kwargs)
        return {"passed": True, "defects": [], "console_errors": [], "device_results": []}

    @contextlib.contextmanager
    def page(workspace_dir):
        opened.append(workspace_dir)
        yield fresh_page.FreshPage(url="http://door", api_url="http://api")

    def review(**kwargs):
        kwargs["audit"]()
        return {"verdict": "fine", "problems": [], "edits": [], "not_repaired": [], "claims": [], "attempts": 1,
                "error": None}

    monkeypatch.setattr(qa_auditor, "run_responsive_qa_audit", audit)
    page_gates.run_page_gates(workspace_dir=str(tmp_path), pitch="p", presentation={"files": ["x.tsx"]},
                              ux_blueprint="", review=review, page=page)

    assert opened == [str(tmp_path)] and len(audited) == 2
    for kwargs in audited:
        assert kwargs["url"] == "http://door" and kwargs["api_ready_url"] == "http://api/openapi.json"
