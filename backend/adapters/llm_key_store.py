"""The users' LLM keys at rest: encrypted with PROVABLE_KEY_SECRET, in a file of their own outside the workspace.

Generated code runs on the same disk, so the file is only ever ciphertext. Each sealed value names its owner, so a row
copied onto another user's is refused, not spent. A workspace reset leaves the file alone.
"""
import abc
import json
import os
import sqlite3
from typing import Dict, Optional

from cryptography.fernet import Fernet, InvalidToken

from llm_credentials import Credential


class KeyStoreError(Exception):
    """The store has no usable secret, or a stored key cannot be read as its owner's."""


class AbstractLlmKeyStore(abc.ABC):
    @abc.abstractmethod
    def save(self, user_id: str, provider: str, api_key: str) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def load(self, user_id: str) -> Optional[Credential]:
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, user_id: str) -> None:
        raise NotImplementedError


class SqliteLlmKeyStore(AbstractLlmKeyStore):
    def __init__(self, path: str, secret: str):
        try:
            self._fernet = Fernet(secret.encode())
        except ValueError as err:
            raise KeyStoreError("PROVABLE_KEY_SECRET is missing or is not a Fernet key.") from err
        self._path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS llm_keys (user_id TEXT PRIMARY KEY, sealed TEXT NOT NULL)")
        os.chmod(path, 0o600)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self._path)

    def save(self, user_id: str, provider: str, api_key: str) -> None:
        sealed = self._fernet.encrypt(json.dumps({"user_id": user_id, "provider": provider, "api_key": api_key}).encode())
        with self._connect() as db:
            db.execute("INSERT OR REPLACE INTO llm_keys (user_id, sealed) VALUES (?, ?)", (user_id, sealed.decode()))

    def load(self, user_id: str) -> Optional[Credential]:
        with self._connect() as db:
            row = db.execute("SELECT sealed FROM llm_keys WHERE user_id = ?", (user_id,)).fetchone()
        if row is None:
            return None
        try:
            stored = json.loads(self._fernet.decrypt(row[0].encode()))
        except InvalidToken as err:
            raise KeyStoreError("The stored key cannot be read: save it again.") from err
        if stored["user_id"] != user_id:
            raise KeyStoreError("The stored key belongs to someone else: save your own again.")
        return Credential(user_id=user_id, provider=stored["provider"], api_key=stored["api_key"])

    def delete(self, user_id: str) -> None:
        with self._connect() as db:
            db.execute("DELETE FROM llm_keys WHERE user_id = ?", (user_id,))


class FakeLlmKeyStore(AbstractLlmKeyStore):
    def __init__(self) -> None:
        self._keys: Dict[str, Credential] = {}

    def save(self, user_id: str, provider: str, api_key: str) -> None:
        self._keys[user_id] = Credential(user_id=user_id, provider=provider, api_key=api_key)

    def load(self, user_id: str) -> Optional[Credential]:
        return self._keys.get(user_id)

    def delete(self, user_id: str) -> None:
        self._keys.pop(user_id, None)
