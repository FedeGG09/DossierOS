from __future__ import annotations

from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, status

from app.core.config import settings


@lru_cache(maxsize=1)
def get_jwks_client() -> PyJWKClient:
    jwks_url = f"{settings.supabase_url.rstrip('/')}/auth/v1/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def extract_bearer_token(authorization_header: str | None) -> str | None:
    if not authorization_header:
        return None
    parts = authorization_header.split()
    if len(parts) != 2:
        return None
    scheme, token = parts
    if scheme.lower() != "bearer":
        return None
    return token.strip() or None


def verify_supabase_jwt(token: str) -> dict[str, Any]:
    try:
        signing_key = get_jwks_client().get_signing_key_from_jwt(token).key
        decoded = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        if "sub" not in decoded:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT sin claim sub")
        return decoded
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="JWT inválido o vencido")
