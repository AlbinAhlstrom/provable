"""Verifies Clerk session tokens (RS256 JWTs) against the issuer's published keys."""
from typing import Callable

import jwt


class AuthError(Exception):
    """The token is missing, malformed, expired, mis-signed or from another issuer."""


class ClerkVerifier:
    def __init__(self, issuer: str, key_resolver: Callable[[str], object]):
        self._issuer = issuer.rstrip("/")
        self._key_resolver = key_resolver

    @classmethod
    def from_issuer(cls, issuer: str) -> "ClerkVerifier":
        """Fetches (and caches) the signing keys from the issuer's JWKS endpoint."""
        client = jwt.PyJWKClient(issuer.rstrip("/") + "/.well-known/jwks.json", cache_keys=True)
        return cls(issuer, lambda token: client.get_signing_key_from_jwt(token).key)

    def verify(self, token: str) -> str:
        """Returns the Clerk user id (`sub`) of a valid token."""
        try:
            key = self._key_resolver(token)
            claims = jwt.decode(
                token, key, algorithms=["RS256"], issuer=self._issuer,
                options={"require": ["exp", "iss", "sub"], "verify_aud": False},
            )
        except (jwt.PyJWTError, jwt.PyJWKClientError) as err:
            raise AuthError(str(err)) from err
        return claims["sub"]
