"""Holds the signed-in user's LLM key for a whole writing request, the background work after its answer included.

An ASGI middleware, because a response's background tasks run inside the call to the app here, while a dependency ends
before them. Reads never hold: nothing that reads spends, and a user watches a running build through them. A request
without a valid token goes on to `require_user`, which answers 401.
"""
from typing import Callable, Optional

from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse

import llm_credentials
from adapters.llm_key_store import AbstractLlmKeyStore, KeyStoreError
from entrypoints.auth import require_user
from service_layer import llm_keys

_READS = ("GET", "HEAD", "OPTIONS")
_KEY_ROUTES = "/api/llm-key"  # saving a key spends nothing, and must work while someone else's build runs


class LlmKeyLease:
    def __init__(self, app, store: Callable[[], AbstractLlmKeyStore]):
        self._app = app
        self._store = store

    def _credential(self, authorization: Optional[str]) -> Optional[llm_credentials.Credential]:
        try:
            user = require_user(authorization)
        except HTTPException:
            return None
        return llm_keys.credential_for(user, self._store()) if user else None

    async def __call__(self, scope, receive, send) -> None:
        if (scope["type"] != "http" or scope["method"] in _READS or not llm_credentials.enforced()
                or not scope["path"].startswith("/api/") or scope["path"].startswith(_KEY_ROUTES)):
            await self._app(scope, receive, send)
            return
        authorization = dict(scope["headers"]).get(b"authorization", b"").decode("latin-1")
        try:
            credential = await run_in_threadpool(self._credential, authorization or None)
            held = llm_credentials.acquire(credential) if credential else None
        except llm_credentials.EngineBusy as err:
            await JSONResponse({"detail": str(err)}, status_code=409)(scope, receive, send)
            return
        except KeyStoreError as err:
            await JSONResponse({"detail": str(err)}, status_code=503)(scope, receive, send)
            return
        try:
            await self._app(scope, receive, send)
        finally:
            if held:
                llm_credentials.release(held)
