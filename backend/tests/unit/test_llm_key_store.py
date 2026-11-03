"""A user's LLM key rests encrypted, tied to its owner, and is only ever shown by its last characters."""
import sqlite3

import pytest
from cryptography.fernet import Fernet

from adapters.llm_key_store import FakeLlmKeyStore, KeyStoreError, SqliteLlmKeyStore
from service_layer import llm_keys

KEY = "sk-test-0123456789abcdefghij"


@pytest.fixture
def path(tmp_path):
    return str(tmp_path / "keys.db")


def test_a_key_comes_back_for_its_owner_and_rests_unreadable(path):
    store = SqliteLlmKeyStore(path, Fernet.generate_key().decode())
    store.save("user_a", "openai", KEY)
    assert store.load("user_a").api_key == KEY and store.load("user_a").provider == "openai"
    assert store.load("user_b") is None
    with open(path, "rb") as f:
        assert KEY.encode() not in f.read()


def test_a_row_copied_to_another_user_is_refused(path):
    """Generated code shares the engine's disk, so a swapped row must not let one user spend another's key."""
    store = SqliteLlmKeyStore(path, Fernet.generate_key().decode())
    store.save("user_a", "openai", KEY)
    store.save("user_b", "openai", "sk-other-0123456789abcdefgh")
    with sqlite3.connect(path) as db:
        stolen = db.execute("SELECT sealed FROM llm_keys WHERE user_id='user_a'").fetchone()[0]
        db.execute("UPDATE llm_keys SET sealed=? WHERE user_id='user_b'", (stolen,))
    with pytest.raises(KeyStoreError):
        store.load("user_b")


def test_a_store_without_a_usable_secret_fails_loudly(path):
    with pytest.raises(KeyStoreError):
        SqliteLlmKeyStore(path, "")
    with pytest.raises(KeyStoreError):
        SqliteLlmKeyStore(path, "not-a-fernet-key")


def test_saving_replaces_and_deleting_removes(path):
    store = SqliteLlmKeyStore(path, Fernet.generate_key().decode())
    store.save("user_a", "openai", KEY)
    store.save("user_a", "gemini", "AIza-0123456789abcdefghij")
    assert store.load("user_a").provider == "gemini"
    store.delete("user_a")
    assert store.load("user_a") is None


def test_status_shows_the_provider_and_last_characters_only():
    keys = FakeLlmKeyStore()
    llm_keys.save_key("user_a", "openai", f"  {KEY}\n", keys)
    status = llm_keys.key_status("user_a", keys)
    assert status == {"managed": True, "configured": True, "provider": "openai", "last4": "ghij", "house": False,
                      "providers": list(llm_keys.USER_PROVIDERS)}
    assert KEY not in str(status)


@pytest.mark.parametrize("provider, api_key", [("azure", KEY), ("anthropic-opus", KEY), ("openai", "short"),
                                               ("openai", "two words 0123456789abcdef"), ("openai", "k" * 600)])
def test_a_key_no_provider_could_use_is_refused(provider, api_key):
    with pytest.raises(llm_keys.InvalidKey):
        llm_keys.save_key("user_a", provider, api_key, FakeLlmKeyStore())


def test_the_credential_of_a_house_user_needs_no_key(monkeypatch):
    monkeypatch.setenv("LLM_HOUSE_USERS", "owner, other_owner")
    credential = llm_keys.credential_for("other_owner", FakeLlmKeyStore())
    assert credential.house and credential.api_key == ""
    assert llm_keys.key_status("owner", FakeLlmKeyStore())["configured"] is True


def test_the_credential_of_a_user_without_a_key_has_none(monkeypatch):
    monkeypatch.delenv("LLM_HOUSE_USERS", raising=False)
    credential = llm_keys.credential_for("user_a", FakeLlmKeyStore())
    assert not credential.house and credential.api_key == ""
    assert llm_keys.key_status("user_a", FakeLlmKeyStore())["configured"] is False
