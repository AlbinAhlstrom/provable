"""The signed-in user's own LLM key. A key goes in here and never comes back; only its ending is shown."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

import llm_credentials
from adapters.llm_key_store import KeyStoreError
from entrypoints.auth import require_user
from service_layer import llm_keys
from service_layer.llm_keys import key_store

router = APIRouter(prefix="/api/llm-key", tags=["LLM Key"])


class SaveKeyRequest(BaseModel):
    provider: str
    api_key: str


def _store():
    try:
        return key_store()
    except KeyStoreError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err


def _signed_in(user: Optional[str]) -> str:
    if not llm_credentials.enforced() or user is None:
        raise HTTPException(status_code=409, detail="This engine runs on its own .env settings.")
    return user


@router.get("")
def get_key(user: Optional[str] = Depends(require_user)):
    if not llm_credentials.enforced() or user is None:
        return {"managed": False}
    try:
        return llm_keys.key_status(user, _store())
    except KeyStoreError as err:
        raise HTTPException(status_code=503, detail=str(err)) from err


@router.put("")
def put_key(req: SaveKeyRequest, user: Optional[str] = Depends(require_user)):
    user = _signed_in(user)
    keys = _store()
    try:
        llm_keys.save_key(user, req.provider, req.api_key, keys)
    except llm_keys.InvalidKey as err:
        raise HTTPException(status_code=422, detail=str(err)) from err
    return llm_keys.key_status(user, keys)


@router.delete("")
def delete_key(user: Optional[str] = Depends(require_user)):
    user = _signed_in(user)
    keys = _store()
    llm_keys.delete_key(user, keys)
    return llm_keys.key_status(user, keys)
