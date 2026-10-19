"""
The page as a new visitor meets it: the app's API started afresh, reading and saving nothing, and an address where
`/api/` is that API and everything else the running page.

QA and the visual review judge the page through it (page_gates.py). The running preview's own API keeps what was
saved while the app was built: a record made by the class the skeleton wrote, before the domain round gave it its
starting state, or one a person made trying the preview. A page opened on such a record is judged on a state no new
visitor meets. The page tests' harness reaches the page the same way, from inside the generated app
(templates/page_test_conftest.py.tmpl).

The page's reload socket is carried through as it is: refused at the door, the browser logs it as a severe error.
"""

import contextlib
import http.client
import os
import socket
import subprocess
import sys
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Iterator
from urllib.parse import urlsplit

from onboarding.qa_auditor import wait_until_answering

PREVIEW_URL = "http://localhost:5174"
API_START_TIMEOUT_S = 30.0
# Hop-by-hop headers, and those the door sets itself
_NOT_PASSED_ON = {"connection", "keep-alive", "transfer-encoding", "content-length", "host", "accept-encoding", "upgrade"}


@dataclass(frozen=True)
class FreshPage:
    url: str       # where the browser opens the page
    api_url: str   # the fresh API itself

    @property
    def api_ready_url(self) -> str:
        return self.api_url + "/openapi.json"


def _free_port() -> int:
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


def _pipe(source: socket.socket, target: socket.socket) -> None:
    try:
        while True:
            data = source.recv(65536)
            if not data:
                break
            target.sendall(data)
    except OSError:
        pass
    finally:
        with contextlib.suppress(OSError):
            target.shutdown(socket.SHUT_WR)


def _door(api_url: str, page_url: str) -> ThreadingHTTPServer:
    class Door(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *args):
            pass

        def _target(self):
            return urlsplit(api_url if urlsplit(self.path).path.startswith("/api/") else page_url)

        def _tunnel(self) -> None:
            """A request to switch to a socket: the connection is handed to the page as it is, both ways."""
            target = self._target()
            upstream = socket.create_connection((target.hostname, target.port), timeout=30)
            upstream.settimeout(None)
            self.connection.settimeout(None)
            head = "".join(f"{name}: {value}\r\n" for name, value in self.headers.items() if name.lower() != "host")
            upstream.sendall(f"{self.requestline}\r\nHost: {target.netloc}\r\n{head}\r\n".encode("latin-1"))
            back = threading.Thread(target=_pipe, args=(upstream, self.connection), daemon=True)
            back.start()
            _pipe(self.connection, upstream)
            back.join()
            upstream.close()
            self.close_connection = True

        def _pass_on(self) -> None:
            if (self.headers.get("Upgrade") or "").lower() == "websocket":
                self._tunnel()
                return
            target = self._target()
            length = int(self.headers.get("Content-Length") or 0)
            asked = self.rfile.read(length) if length else None
            headers = {name: value for name, value in self.headers.items() if name.lower() not in _NOT_PASSED_ON}
            upstream = http.client.HTTPConnection(target.hostname, target.port, timeout=30)
            try:
                upstream.request(self.command, self.path, body=asked, headers={**headers, "Host": target.netloc})
                answer = upstream.getresponse()
                body = answer.read()
            except OSError as err:
                self.send_error(502, f"{target.netloc} did not answer: {err}")
                return
            finally:
                upstream.close()
            self.send_response(answer.status)
            for name, value in answer.getheaders():
                if name.lower() not in _NOT_PASSED_ON:
                    self.send_header(name, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _pass_on

    class Server(ThreadingHTTPServer):
        daemon_threads = True

        def handle_error(self, request, client_address):
            if not isinstance(sys.exc_info()[1], ConnectionError):  # a browser closing a connection is no fault
                super().handle_error(request, client_address)

    server = Server(("127.0.0.1", 0), Door)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


@contextlib.contextmanager
def fresh_page(workspace_dir: str, page_url: str = PREVIEW_URL) -> Iterator[FreshPage]:
    """Starts the app's API with nothing saved and opens the door to the page; both close when the block ends.
    Raises RuntimeError, with what the API said, when it does not start: nothing is judged on another API."""
    port = _free_port()
    api_url = f"http://127.0.0.1:{port}"
    log_path = os.path.join(workspace_dir, ".qa_reports", "fresh_api.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w", encoding="utf-8") as log:
        api = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "src.app:app", "--host", "127.0.0.1", "--port", str(port),
             "--log-level", "warning"],
            cwd=workspace_dir, env={**os.environ, "APP_DATA_DIR": ""}, stdout=log, stderr=subprocess.STDOUT)
        door = None
        try:
            if not wait_until_answering(api_url + "/openapi.json", timeout_s=API_START_TIMEOUT_S) or api.poll() is not None:
                log.flush()
                with open(log_path, encoding="utf-8") as said:
                    raise RuntimeError("The app's API did not start for the page's judgement:\n" + said.read()[-1500:])
            door = _door(api_url, page_url)
            yield FreshPage(url=f"http://127.0.0.1:{door.server_address[1]}", api_url=api_url)
        finally:
            if door is not None:
                door.shutdown()
                door.server_close()
            api.terminate()
            try:
                api.wait(timeout=10)
            except subprocess.TimeoutExpired:
                api.kill()
                api.wait()
