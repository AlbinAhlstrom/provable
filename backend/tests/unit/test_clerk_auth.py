"""Clerk session tokens: verified against the issuer's public keys; auth is off when Clerk is not configured."""
import time

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from adapters.clerk_auth import ClerkVerifier, AuthError
from entrypoints.auth import require_user

ISSUER = "https://clerk.example.test"


@pytest.fixture(autouse=True)
def _reset_verifier():
    yield
    import entrypoints.auth as auth
    auth.set_verifier(None)


@pytest.fixture(scope="module")
def keys():
    return rsa.generate_private_key(public_exponent=65537, key_size=2048), rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _token(key, sub="user_1", iss=ISSUER, exp_in=300):
    return jwt.encode({"sub": sub, "iss": iss, "exp": int(time.time()) + exp_in}, key, algorithm="RS256")


def _verifier(key):
    return ClerkVerifier(issuer=ISSUER, key_resolver=lambda token: key.public_key())


def test_valid_token_returns_user_id(keys):
    assert _verifier(keys[0]).verify(_token(keys[0])) == "user_1"


def test_wrong_signature_rejected(keys):
    with pytest.raises(AuthError):
        _verifier(keys[0]).verify(_token(keys[1]))


def test_expired_token_rejected(keys):
    with pytest.raises(AuthError):
        _verifier(keys[0]).verify(_token(keys[0], exp_in=-10))


def test_wrong_issuer_rejected(keys):
    with pytest.raises(AuthError):
        _verifier(keys[0]).verify(_token(keys[0], iss="https://evil.test"))


def _client(verifier):
    app = FastAPI()
    app.dependency_overrides = {}

    @app.get("/api/me")
    def me(user=Depends(require_user)):
        return {"user": user}

    import entrypoints.auth as auth
    auth.set_verifier(verifier)
    return TestClient(app)


def test_auth_off_when_unconfigured():
    c = _client(None)
    assert c.get("/api/me").json() == {"user": None}


def test_missing_or_bad_header_is_401(keys):
    c = _client(_verifier(keys[0]))
    assert c.get("/api/me").status_code == 401
    assert c.get("/api/me", headers={"Authorization": "Bearer junk"}).status_code == 401


def test_good_header_passes(keys):
    c = _client(_verifier(keys[0]))
    r = c.get("/api/me", headers={"Authorization": f"Bearer {_token(keys[0])}"})
    assert r.json() == {"user": "user_1"}
