"""End to end through HTTP: a signed-in user's key is saved, and it covers their whole request, background work included."""
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

import llm_credentials
import llm_provider
from adapters.clerk_auth import ClerkVerifier
from adapters.llm_key_store import FakeLlmKeyStore
from entrypoints import llm_lease
from entrypoints.auth import require_user, set_verifier
from entrypoints.routers import llm_key

ISSUER = "https://clerk.example.test"
PRIVATE = rsa.generate_private_key(public_exponent=65537, key_size=2048)
KEY = "sk-test-0123456789abcdefghij"


def _headers(user):
    token = jwt.encode({"sub": user, "iss": ISSUER, "exp": int(time.time()) + 300}, PRIVATE, algorithm="RS256")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seen():
    return []


@pytest.fixture
def client(monkeypatch, seen):
    monkeypatch.setenv("CLERK_ISSUER", ISSUER)
    monkeypatch.delenv("LLM_HOUSE_USERS", raising=False)
    set_verifier(ClerkVerifier(issuer=ISSUER, key_resolver=lambda token: PRIVATE.public_key()))
    store = FakeLlmKeyStore()
    monkeypatch.setattr(llm_key, "key_store", lambda: store)

    work = APIRouter()

    @work.post("/api/work")
    def run(background: BackgroundTasks):
        seen.append(llm_provider.connection().api_key)
        background.add_task(lambda: seen.append(llm_provider.connection().api_key))
        return {"ok": True}

    app = FastAPI()
    app.add_middleware(llm_lease.LlmKeyLease, store=lambda: store)
    app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
    app.include_router(llm_key.router, dependencies=[Depends(require_user)])
    app.include_router(work, dependencies=[Depends(require_user)])
    yield TestClient(app)
    set_verifier(None)
    llm_credentials.reset()


def test_a_saved_key_answers_with_its_ending_and_never_in_full(client):
    saved = client.put("/api/llm-key", headers=_headers("user_a"), json={"provider": "openai", "api_key": KEY})
    assert saved.status_code == 200 and KEY not in saved.text
    status = client.get("/api/llm-key", headers=_headers("user_a")).json()
    assert (status["configured"], status["provider"], status["last4"]) == (True, "openai", "ghij")


def test_one_users_key_is_invisible_to_another(client):
    client.put("/api/llm-key", headers=_headers("user_a"), json={"provider": "openai", "api_key": KEY})
    assert client.get("/api/llm-key", headers=_headers("user_b")).json()["configured"] is False


def test_a_removed_key_is_gone(client):
    client.put("/api/llm-key", headers=_headers("user_a"), json={"provider": "openai", "api_key": KEY})
    assert client.delete("/api/llm-key", headers=_headers("user_a")).status_code == 200
    assert client.get("/api/llm-key", headers=_headers("user_a")).json()["configured"] is False


def test_a_refused_key_says_why(client):
    answer = client.put("/api/llm-key", headers=_headers("user_a"), json={"provider": "azure", "api_key": KEY})
    assert answer.status_code == 422 and "azure" in answer.json()["detail"]


def test_no_token_no_key_routes(client):
    assert client.get("/api/llm-key").status_code == 401
    assert client.put("/api/llm-key", json={"provider": "openai", "api_key": KEY}).status_code == 401


def test_the_key_covers_the_request_and_its_background_work_then_leaves(client, seen):
    client.put("/api/llm-key", headers=_headers("user_a"), json={"provider": "openai", "api_key": KEY})
    assert client.post("/api/work", headers=_headers("user_a"), json={}).status_code == 200
    assert seen == [KEY, KEY]
    assert llm_credentials.current() is None


def test_a_second_user_gets_409_with_cors_headers_while_a_run_is_held(client):
    llm_credentials.acquire(llm_credentials.Credential(user_id="user_a", provider="openai", api_key=KEY))
    answer = client.post("/api/work", headers={**_headers("user_b"), "Origin": "https://studio.example"}, json={})
    assert answer.status_code == 409 and answer.headers.get("access-control-allow-origin") == "*"


def test_reading_is_never_refused_by_a_running_build(client):
    llm_credentials.acquire(llm_credentials.Credential(user_id="user_a", provider="openai", api_key=KEY))
    assert client.get("/api/llm-key", headers=_headers("user_b")).status_code == 200


def test_saving_a_key_is_never_refused_by_a_running_build(client):
    llm_credentials.acquire(llm_credentials.Credential(user_id="user_a", provider="openai", api_key=KEY))
    answer = client.put("/api/llm-key", headers=_headers("user_b"), json={"provider": "openai", "api_key": KEY})
    assert answer.status_code == 200


def test_a_bad_token_is_left_to_the_login_check(client):
    assert client.post("/api/work", headers={"Authorization": "Bearer nonsense"}, json={}).status_code == 401
    assert llm_credentials.current() is None


def test_a_local_engine_has_no_key_routes_to_fill(monkeypatch):
    monkeypatch.delenv("CLERK_ISSUER", raising=False)
    store = FakeLlmKeyStore()
    monkeypatch.setattr(llm_key, "key_store", lambda: store)
    app = FastAPI()
    app.include_router(llm_key.router)
    local = TestClient(app)
    assert local.get("/api/llm-key").json()["managed"] is False
    assert local.put("/api/llm-key", json={"provider": "openai", "api_key": KEY}).status_code == 409
