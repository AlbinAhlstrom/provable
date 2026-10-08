"""Seed data stage: sample records for content shown to the audience, proved against the generated domain."""

import json
import subprocess
import sys

import pytest

import agent_orchestrator
from onboarding import seed_data
from onboarding.router_engine import AudienceRole, DomainStructureSchema, EntitySpec
from onboarding.skeleton_builder import build_and_write_skeleton

STRUCTURE = DomainStructureSchema(domain_name="Site", entities=[
    EntitySpec(name="ServiceOffering", audience_role=AudienceRole.SHOWN, attributes=[
        {"name": "id", "type": "string"}, {"name": "title", "type": "string"},
        {"name": "base_hourly_rate", "type": "float"}]),
    EntitySpec(name="ClientInquiry", audience_role=AudienceRole.CREATED, attributes=[
        {"name": "id", "type": "string"}, {"name": "parent_name", "type": "string"}]),
])

GOOD = {"records": {"ServiceOffering": [
    {"id": "infant-care", "title": "Infant care", "base_hourly_rate": 32.0},
    {"id": "after-school", "title": "After-school care", "base_hourly_rate": 28.0}]}}


@pytest.fixture
def workspace(tmp_path):
    build_and_write_skeleton(STRUCTURE, target_dir=str(tmp_path))
    return tmp_path


def _llm(monkeypatch, *answers):
    calls = []

    def fake(prompt, stage="general", **kwargs):
        calls.append(prompt)
        answer = answers[min(len(calls), len(answers)) - 1]
        return answer if isinstance(answer, str) else json.dumps(answer)

    monkeypatch.setattr(seed_data.agent_orchestrator, "call_gemini", fake)
    return calls


def _run(workspace):
    return seed_data.synthesize_seed_data("a childcare site", STRUCTURE, [], str(workspace))


def test_valid_records_are_written_and_served_by_the_generated_api(workspace, monkeypatch):
    """Verify seeds reach the API: the file is written and the generated router lists the records.

    id: TST-SEED-001
    Given: A skeleton and an answer with two valid offerings
    When: Seed data is synthesized and the workspace API is imported afresh
    Then: src/seed_data.json holds them and GET /api/service_offerings returns both; the created entity stays empty
    """
    calls = _llm(monkeypatch, GOOD)
    result = _run(workspace)
    assert result["success"] is True and len(calls) == 1
    assert json.loads((workspace / "src" / "seed_data.json").read_text(encoding="utf-8")) == GOOD["records"]
    assert "ServiceOffering" in calls[0] and "ClientInquiry" not in calls[0].split("Entities to fill")[1].split("Rules the records")[0]

    script = ("from fastapi.testclient import TestClient\nfrom src.app import app\nc = TestClient(app)\n"
              "import json\nprint(json.dumps([c.get('/api/service_offerings').json(), c.get('/api/client_inquiries').json()]))")
    out = subprocess.run([sys.executable, "-c", script], cwd=workspace, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    offerings, inquiries = json.loads(out.stdout.strip().splitlines()[-1])
    assert [o["id"] for o in offerings] == ["infant-care", "after-school"] and inquiries == []


def test_the_records_are_written_knowing_what_day_it_is(workspace, monkeypatch):
    """Verify the model is told today's date, so a date the audience acts on (an open shift) is not in the past.

    id: TST-SEED-TODAY
    Given: A skeleton and a valid answer
    When: Seed data is synthesized
    Then: The prompt states today's date and asks for dates the audience acts on to be upcoming
    """
    from datetime import date
    calls = _llm(monkeypatch, GOOD)
    assert _run(workspace)["success"] is True
    assert f"Today is {date.today().isoformat()}" in calls[0]
    assert "the next two weeks" in calls[0]


def test_a_rejected_record_is_fed_back_once_and_the_fix_is_accepted(workspace, monkeypatch):
    """Verify the one verdict-fed retry: the domain's rejection reaches the model, the corrected answer is written.

    id: TST-SEED-002
    Given: A first answer whose record lacks a required attribute, then a valid one
    When: Seed data is synthesized
    Then: Two attempts are recorded, the second prompt names the rejected record, and the file holds the corrected data
    """
    bad = {"records": {"ServiceOffering": [{"id": "infant-care", "title": "Infant care"}]}}
    calls = _llm(monkeypatch, bad, GOOD)
    result = _run(workspace)
    assert result["success"] is True and [a["approved"] for a in result["attempts"]] == [False, True]
    assert "infant-care" in calls[1] and "rejected the previous records" in calls[1]
    assert (workspace / "src" / "seed_data.json").exists()


def test_two_rejections_fail_loudly_and_write_nothing(workspace, monkeypatch):
    """Verify no third attempt and no half-valid file.

    id: TST-SEED-003
    Given: Two consecutive invalid answers
    When: Seed data is synthesized
    Then: The stage fails naming the record, exactly two calls were made, and no seed file exists
    """
    bad = {"records": {"ServiceOffering": [{"id": "x", "title": "x"}]}}
    calls = _llm(monkeypatch, bad, bad, GOOD)
    result = _run(workspace)
    assert result["success"] is False and "twice" in result["error"] and "ServiceOffering[0]" in result["error"]
    assert len(calls) == 2 and not (workspace / "src" / "seed_data.json").exists()


@pytest.mark.parametrize("answer, expected", [
    ("", "empty response"),
    ("not json at all", "not usable seed data"),
    ({"records": {**GOOD["records"], "ClientInquiry": [{"id": "1", "parent_name": "x"}]}}, "not shown to the audience"),
    ({"records": {}}, "no records for: ServiceOffering"),
])
def test_provider_and_parse_errors_are_not_retried(workspace, monkeypatch, answer, expected):
    """Verify errors that are not a domain verdict fail at once with their reason.

    id: TST-SEED-004
    Given: An empty answer, non-JSON, records for the wrong entity, or no records
    When: Seed data is synthesized
    Then: One call only, success False, and the reason names the problem
    """
    agent_orchestrator.LAST_LLM_ERROR = None
    calls = _llm(monkeypatch, answer, GOOD)
    result = _run(workspace)
    assert result["success"] is False and expected in result["error"] and len(calls) == 1


def test_a_product_with_no_shown_entities_needs_no_seed(tmp_path, monkeypatch):
    """Verify the stage is a no-op for products that show the audience nothing authored.

    id: TST-SEED-005
    Given: A structure with only a created entity
    When: Seed data is synthesized
    Then: It succeeds as skipped, with no LLM call and no file
    """
    calls = _llm(monkeypatch, GOOD)
    structure = DomainStructureSchema(domain_name="Game", entities=[EntitySpec(name="Session", audience_role=AudienceRole.CREATED)])
    result = seed_data.synthesize_seed_data("a game", structure, [], str(tmp_path))
    assert result["success"] is True and result["skipped"] and calls == [] and result["files"] == []


def test_the_generated_api_assigns_the_id_of_a_record_the_audience_creates(workspace):
    """Verify a visitor's form can create a record: the browser does not know an id, so the server assigns one
    (the generated create endpoint demanded `id` from the client and every form submission was rejected).

    id: TST-SEED-CREATE
    Given: A generated API for an entity the audience creates
    When: Two records are posted without an id
    Then: Both are created with different ids and both are listed
    """
    script = ("from fastapi.testclient import TestClient\nfrom src.app import app\nc = TestClient(app)\n"
              "import json\n"
              "a = c.post('/api/client_inquiries', json={'parent_name': 'Ada'})\n"
              "b = c.post('/api/client_inquiries', json={'parent_name': 'Bo'})\n"
              "print(json.dumps([a.status_code, b.status_code, a.json(), b.json(), c.get('/api/client_inquiries').json()]))")
    out = subprocess.run([sys.executable, "-c", script], cwd=workspace, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    status_a, status_b, first, second, listed = json.loads(out.stdout.strip().splitlines()[-1])
    assert (status_a, status_b) == (201, 201), (first, second)
    assert first["id"] and second["id"] and first["id"] != second["id"]
    assert sorted(i["parent_name"] for i in listed) == ["Ada", "Bo"]


def test_the_generated_api_removes_a_record(workspace):
    """Verify a stored record can be removed again (the QA form check removes what it created).

    id: TST-SEED-DELETE
    Given: A generated API with one created record
    When: The record is deleted, then deleted again
    Then: The first delete answers 204 and the record is gone; the second answers 404
    """
    script = ("from fastapi.testclient import TestClient\nfrom src.app import app\nc = TestClient(app)\n"
              "import json\n"
              "made = c.post('/api/client_inquiries', json={'parent_name': 'Ada'}).json()\n"
              "first = c.delete('/api/client_inquiries/' + made['id'])\n"
              "second = c.delete('/api/client_inquiries/' + made['id'])\n"
              "print(json.dumps([first.status_code, second.status_code, c.get('/api/client_inquiries').json()]))")
    out = subprocess.run([sys.executable, "-c", script], cwd=workspace, capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert json.loads(out.stdout.strip().splitlines()[-1]) == [204, 404, []]
