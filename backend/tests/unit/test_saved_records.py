"""A generated app keeps its records when its API restarts (skeleton_builder: `src/adapters/record_store.py`).

The generated API holds its records in memory and restarts every time the build writes a rule, so whatever a user
added while watching the build disappeared. Each router now saves its records to a file beside the app and reads them
back on its first request. Tests of the generated app run without the file (`tests/conftest.py`), and a new build
starts empty.
"""
import json
import os
import subprocess
import sys
import time
import types

import pytest

from onboarding.router_engine import AudienceRole, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import DATA_DIR, build_and_write_skeleton, generate_record_store_module

STRUCTURE = DomainStructureSchema(domain_name="Salon", entities=[
    EntitySpec(name="Booking", audience_role=AudienceRole.CREATED,
               attributes=[{"name": "id", "type": "string"}, {"name": "guest", "type": "string"}]),
])

CLIENT = "from fastapi.testclient import TestClient\nfrom src.app import app\nimport json\nc = TestClient(app)\n"


def _api(tmp_path, script, env=None):
    """Runs `script` in a fresh process, the way a restarted API starts with nothing in memory."""
    out = subprocess.run([sys.executable, "-c", CLIENT + script], cwd=tmp_path, capture_output=True, text=True,
                         env={**os.environ, **(env or {})})
    assert out.returncode == 0, out.stderr
    return _named(json.loads(out.stdout.strip().splitlines()[-1]))


def _named(value):
    """A booking as its id and guest (the generated class also carries bookkeeping fields of its own)."""
    if isinstance(value, list):
        return [_named(v) for v in value]
    return {"id": value["id"], "guest": value["guest"]} if isinstance(value, dict) else value


def test_a_record_survives_a_restart_of_the_api(tmp_path):
    """Verify what a user added is still there after the API restarts.

    id: TST-SAVED-001
    Given: A generated app in which a booking was created and then changed by nothing else
    When: A fresh process lists the bookings
    Then: The booking is there
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    _api(tmp_path, "print(json.dumps(c.post('/api/bookings', json={'id': 'b1', 'guest': 'Ada'}).status_code))")
    assert _api(tmp_path, "print(json.dumps(c.get('/api/bookings').json()))") == [{"id": "b1", "guest": "Ada"}]


def test_a_removed_starting_record_stays_removed(tmp_path):
    """Verify the starting content is added once, not again on every restart.

    id: TST-SAVED-002
    Given: A generated app with one seeded booking, which a user then deletes
    When: A fresh process lists the bookings
    Then: The list is empty (the seed file did not change, so it is not applied again)
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    (tmp_path / "src" / "seed_data.json").write_text(json.dumps({"Booking": [{"id": "seed-1", "guest": "Grace"}]}), encoding="utf-8")
    seeded = _api(tmp_path, "print(json.dumps([c.get('/api/bookings').json(), c.delete('/api/bookings/seed-1').status_code]))")
    assert seeded == [[{"id": "seed-1", "guest": "Grace"}], 204]
    assert _api(tmp_path, "print(json.dumps(c.get('/api/bookings').json()))") == []


def test_the_generated_apps_own_tests_never_touch_the_saved_records(tmp_path):
    """Verify a test run of the generated app neither reads nor writes what the running app saved.

    id: TST-SAVED-003
    Given: A generated app with a saved booking, and the environment its tests/conftest.py sets
    When: A process with that environment lists the bookings and creates one
    Then: It sees none of the saved records, and the saved file is unchanged
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    _api(tmp_path, "print(json.dumps(c.post('/api/bookings', json={'id': 'b1', 'guest': 'Ada'}).status_code))")
    conftest = (tmp_path / "tests" / "conftest.py").read_text(encoding="utf-8")
    assert 'os.environ["APP_DATA_DIR"] = ""' in conftest

    seen = _api(tmp_path, "print(json.dumps(c.get('/api/bookings').json()))\n"
                          "c.post('/api/bookings', json={'id': 'test-1', 'guest': 'Test'})", env={"APP_DATA_DIR": ""})
    assert seen == []
    assert _api(tmp_path, "print(json.dumps(c.get('/api/bookings').json()))") == [{"id": "b1", "guest": "Ada"}]


def test_a_record_the_class_no_longer_accepts_is_left_out_and_the_api_stays_up(tmp_path):
    """Verify a saved record from before the class changed shape does not take the API down.

    id: TST-SAVED-004
    Given: A saved file holding one valid booking and one with a field the class does not have
    When: A fresh process lists the bookings
    Then: The valid booking is served and the other is left out
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    store = tmp_path / DATA_DIR
    store.mkdir()
    (store / "bookings.json").write_text(json.dumps({"seed_mtime": None, "records": [
        {"id": "b1", "guest": "Ada"}, {"id": "b2", "guest": "Bo", "no_such_field": 1}]}), encoding="utf-8")
    assert _api(tmp_path, "print(json.dumps(c.get('/api/bookings').json()))") == [{"id": "b1", "guest": "Ada"}]


def test_a_new_build_starts_without_the_previous_apps_records(tmp_path):
    """Verify records saved by the app that was there before are not carried into a newly built one.

    id: TST-SAVED-005
    Given: A generated app with a saved booking
    When: The skeleton is built again
    Then: The saved records are gone
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    _api(tmp_path, "print(json.dumps(c.post('/api/bookings', json={'id': 'b1', 'guest': 'Ada'}).status_code))")
    assert (tmp_path / DATA_DIR / "bookings.json").exists()
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    assert not (tmp_path / DATA_DIR).exists()


def test_a_new_record_starts_as_its_class_says_not_as_the_form_defaults(tmp_path):
    """Verify fields the client did not send are left to the class, which knows its own starting state.

    id: TST-CREATE-CLASS-DEFAULTS
    Given: A generated app whose Booking class starts every booking with a note of its own, and whose create
           schema gives that field an empty default (as every list of owned parts gets: a chess match was created
           with an empty board because the schema's empty list was passed over the class's starting position)
    When: A booking is created with only its guest, and another with an explicit note
    Then: The first has the class's note, the second the note it was sent
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    domain = tmp_path / "src" / "domain" / "booking.py"
    source = domain.read_text(encoding="utf-8")
    assert "    guest: str\n" in source
    domain.write_text(source.replace("    guest: str\n", "    guest: str\n    notes: List[str] = field(default_factory=lambda: ['welcome'])\n"),
                      encoding="utf-8")
    schemas = tmp_path / "src" / "entrypoints" / "schemas.py"
    schema = schemas.read_text(encoding="utf-8")
    assert "    guest: str\n    id: Optional[str] = None\n" in schema
    schemas.write_text(schema.replace("    guest: str\n    id: Optional[str] = None\n",
                                      "    guest: str\n    id: Optional[str] = None\n    notes: List[str] = Field(default_factory=list)\n"),
                       encoding="utf-8")
    out = subprocess.run([sys.executable, "-c", CLIENT + (
        "a = c.post('/api/bookings', json={'guest': 'Ada'}).json()\n"
        "b = c.post('/api/bookings', json={'guest': 'Bo', 'notes': ['vip']}).json()\n"
        "print(json.dumps([a['notes'], b['notes'], bool(a['id'])]))")], cwd=tmp_path, capture_output=True, text=True,
        env={**os.environ, "APP_DATA_DIR": ""})
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout.strip().splitlines()[-1]) == [["welcome"], ["vip"], True]


def test_a_field_the_class_grew_later_can_be_set_when_a_record_is_created(tmp_path):
    """Verify a record is created with a field its class gained after the API was written, and a field the class
    does not have is refused by name.

    id: TST-CREATE-GROWN-FIELD
    Given: A generated app whose Booking class gained a field while its rules were built (a game gained a switch
           this way; a page test arranged a record with the switch on, the create schema dropped it without a word
           and the rule's light turned red on a page that was right)
    When: A booking is created with that field, and another with a field no booking has
    Then: The first is stored with the field as sent; the second is refused with 422 naming the field
    """
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    domain = tmp_path / "src" / "domain" / "booking.py"
    source = domain.read_text(encoding="utf-8")
    assert "    guest: str\n" in source
    domain.write_text(source.replace("    guest: str\n", "    guest: str\n    reminders: bool = False\n"), encoding="utf-8")
    out = subprocess.run([sys.executable, "-c", CLIENT + (
        "a = c.post('/api/bookings', json={'guest': 'Ada', 'reminders': True})\n"
        "b = c.post('/api/bookings', json={'guest': 'Bo', 'colour': 'red'})\n"
        "print(json.dumps([a.status_code, a.json().get('reminders'), b.status_code, 'colour' in b.text]))")],
        cwd=tmp_path, capture_output=True, text=True, env={**os.environ, "APP_DATA_DIR": ""})
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout.strip().splitlines()[-1]) == [201, True, 422, True]


def _record_store(tmp_path, monkeypatch):
    """The generated record store as a module, saving into `tmp_path`."""
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path))
    store = types.ModuleType("record_store")
    store.__file__ = str(tmp_path / "record_store.py")
    exec(generate_record_store_module(), store.__dict__)
    return store


def test_a_save_waits_for_a_file_another_program_is_holding(tmp_path, monkeypatch):
    """Verify a change is saved when the records file is briefly held by another program.

    id: TST-SAVED-007
    Given: A records file that another program holds open for the first two attempts to put the new one in its
           place (on Windows a file being scanned or read refuses to be replaced; a move in a board game and a
           booking in a salon both answered 500 although the change had been made)
    When: The records are saved
    Then: The save succeeds, the file holds the new records and no half-written file is left behind
    """
    store = _record_store(tmp_path, monkeypatch)
    store.save("bookings", [{"id": "b1"}], None)
    replace, refusals = os.replace, []

    def held_twice(source, target):
        if len(refusals) < 2:
            refusals.append(target)
            raise PermissionError(13, "The file is held by another program")
        replace(source, target)

    monkeypatch.setattr(os, "replace", held_twice)
    monkeypatch.setattr(time, "sleep", lambda seconds: None)
    store.save("bookings", [{"id": "b1"}, {"id": "b2"}], None)
    assert [r["id"] for r in store.load("bookings")["records"]] == ["b1", "b2"]
    assert os.listdir(tmp_path) == ["bookings.json"]


def test_a_save_fails_loudly_when_the_file_stays_held(tmp_path, monkeypatch):
    """Verify a records file that is never released is an error, after a wait of under a second.

    id: TST-SAVED-008
    Given: A records file another program never lets go of
    When: The records are saved
    Then: The save raises the refusal it met, having waited less than a second in all
    """
    store = _record_store(tmp_path, monkeypatch)
    waited = []

    def held(source, target):
        raise PermissionError(13, "The file is held by another program")

    monkeypatch.setattr(os, "replace", held)
    monkeypatch.setattr(time, "sleep", waited.append)
    with pytest.raises(PermissionError):
        store.save("bookings", [{"id": "b1"}], None)
    assert waited and sum(waited) < 1


def test_changes_made_at_the_same_moment_are_all_saved(tmp_path, monkeypatch):
    """Verify two requests that change records at once do not trip over each other's save.

    id: TST-SAVED-009
    Given: A records file, and several requests saving to it at the same moment (a page that opens asks twice at
           once; the saves shared one half-written file, so one of them found it gone and the request answered 500)
    When: They all save
    Then: None fails, the file holds a complete set of records and no half-written file is left behind
    """
    import threading

    store = _record_store(tmp_path, monkeypatch)
    failures, start = [], threading.Barrier(8)

    def save_repeatedly(worker):
        start.wait()
        for turn in range(40):
            try:
                store.save("bookings", [{"id": f"b{worker}-{turn}"}], None)
            except Exception as err:
                failures.append(repr(err))

    threads = [threading.Thread(target=save_repeatedly, args=(n,)) for n in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert failures == []
    assert len(store.load("bookings")["records"]) == 1
    assert os.listdir(tmp_path) == ["bookings.json"]
