"""
Record store: the records of the running app, kept in one JSON file per collection.

The API holds its records in memory and restarts whenever its code changes. Each router saves its collection here
after every change and reads it back on its first request, so a restart loses nothing. `APP_DATA_DIR` names the
folder; set to an empty string (as the tests do) nothing is read or saved.
"""

import json
import os
import threading
import time
from typing import Any, Dict, List, Optional

_DEFAULT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".data")
# Seconds to wait between attempts to replace a records file another program is holding: under a second in all.
_HELD_FILE_WAITS = (0.01, 0.02, 0.05, 0.1, 0.2, 0.4)
# Requests are answered on several threads, and two that change records at the same moment would write the same
# half-finished file: one save at a time.
_saving = threading.Lock()


def _path(collection: str) -> Optional[str]:
    folder = os.environ.get("APP_DATA_DIR", _DEFAULT_DIR)
    return os.path.join(folder, f"{collection}.json") if folder else None


def load(collection: str) -> Dict[str, Any]:
    """The saved records and the modification time of the seed file they already include."""
    path = _path(collection)
    if not path or not os.path.exists(path):
        return {"seed_mtime": None, "records": []}
    with open(path, encoding="utf-8") as saved:
        return json.load(saved)


def save(collection: str, records: List[Dict[str, Any]], seed_mtime: Optional[float]) -> None:
    path = _path(collection)
    if not path:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with _saving:
        with open(path + ".tmp", "w", encoding="utf-8") as out:
            json.dump({"seed_mtime": seed_mtime, "records": records}, out, default=str)
        _put_in_place(path + ".tmp", path)


def _put_in_place(written: str, path: str) -> None:
    """Replaces the records file with the one just written.

    On Windows a file another program has open (a virus scanner, an indexer, an editor) refuses to be replaced for
    as long as it is held, which is a few milliseconds. The change is already made in memory, so the save waits for
    the file to be let go instead of failing the request; a file that stays held is still an error.
    """
    for wait in _HELD_FILE_WAITS:
        try:
            os.replace(written, path)
            return
        except PermissionError:
            time.sleep(wait)
    os.replace(written, path)
