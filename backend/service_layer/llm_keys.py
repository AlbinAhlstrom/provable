"""Use cases of a user's own LLM key: save, show by its ending, remove, and resolve it for a request."""
import os
from typing import Any, Dict, Set

import llm_credentials
from adapters.llm_key_store import AbstractLlmKeyStore, SqliteLlmKeyStore
from config_loader import get_workspace_base
from llm_credentials import Credential

USER_PROVIDERS = ("gemini", "openai", "anthropic")  # a user names a provider, never an endpoint
_MIN_KEY_LENGTH, _MAX_KEY_LENGTH = 20, 512


class InvalidKey(ValueError):
    """No provider could use this key."""


def key_store() -> AbstractLlmKeyStore:
    default = os.path.join(os.path.dirname(os.path.abspath(get_workspace_base())), "provable-keys.db")
    return SqliteLlmKeyStore(os.environ.get("PROVABLE_KEYS_DB") or default,
                             llm_credentials.setting(llm_credentials.KEY_SECRET_SETTING))


def _house_users() -> Set[str]:
    return {user.strip() for user in os.environ.get("LLM_HOUSE_USERS", "").split(",") if user.strip()}


def save_key(user_id: str, provider: str, api_key: str, keys: AbstractLlmKeyStore) -> None:
    api_key = api_key.strip()
    if provider not in USER_PROVIDERS:
        raise InvalidKey(f"{provider!r} is not a provider this engine calls (known: {', '.join(USER_PROVIDERS)}).")
    if not _MIN_KEY_LENGTH <= len(api_key) <= _MAX_KEY_LENGTH or any(char.isspace() for char in api_key):
        raise InvalidKey("That does not look like an API key.")
    keys.save(user_id, provider, api_key)


def delete_key(user_id: str, keys: AbstractLlmKeyStore) -> None:
    keys.delete(user_id)


def credential_for(user_id: str, keys: AbstractLlmKeyStore) -> Credential:
    """What a request of this user runs on; without a key of their own, a call fails and says where to add one."""
    if user_id in _house_users():
        return Credential(user_id=user_id, house=True)
    return keys.load(user_id) or Credential(user_id=user_id)


def key_status(user_id: str, keys: AbstractLlmKeyStore) -> Dict[str, Any]:
    credential = credential_for(user_id, keys)
    return {"managed": True, "configured": credential.house or bool(credential.api_key),
            "provider": credential.provider or None, "last4": credential.api_key[-4:] or None,
            "house": credential.house, "providers": list(USER_PROVIDERS)}
