"""FastAPI dependency that requires a signed-in Clerk user. Off (user is None) when CLERK_ISSUER is unset."""
import os
from typing import Optional

from fastapi import Header, HTTPException

from adapters.clerk_auth import AuthError, ClerkVerifier

_verifier: Optional[ClerkVerifier] = None
_configured = False


def set_verifier(verifier: Optional[ClerkVerifier]) -> None:
    global _verifier, _configured
    _verifier, _configured = verifier, True


def _get_verifier() -> Optional[ClerkVerifier]:
    if not _configured:
        issuer = os.environ.get("CLERK_ISSUER", "").strip()
        set_verifier(ClerkVerifier.from_issuer(issuer) if issuer else None)
    return _verifier


def require_user(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    verifier = _get_verifier()
    if verifier is None:
        return None
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Sign in to use Provable.")
    try:
        return verifier.verify(token)
    except AuthError as err:
        raise HTTPException(status_code=401, detail=f"Invalid session: {err}") from err
