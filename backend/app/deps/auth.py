from __future__ import annotations

import json
from typing import Generator
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings


def get_current_claims(request: Request) -> dict:
    claims = getattr(request.state, "supabase_claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta JWT válido de Supabase")
    return claims


def get_current_user_id(claims: dict = Depends(get_current_claims)) -> UUID:
    try:
        return UUID(str(claims["sub"]))
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Claim sub inválido")


def get_rls_db(
    request: Request,
    db: Session = Depends(get_db),
) -> Generator[Session, None, None]:
    claims = getattr(request.state, "supabase_claims", None)
    if not claims:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Falta JWT válido para abrir sesión RLS")

    claims_json = json.dumps(claims)
    sub = str(claims["sub"])

    db.execute(text("set local role authenticated"))
    db.execute(text("select set_config('request.jwt.claims', :claims, true)"), {"claims": claims_json})
    db.execute(text("select set_config('request.jwt.claim.sub', :sub, true)"), {"sub": sub})

    try:
        yield db
    finally:
        try:
            db.execute(text("reset role"))
            db.commit()
        except Exception:
            db.rollback()


def require_admin(request: Request) -> None:
    if not settings.admin_key:
        return
    incoming = request.headers.get("x-admin-key")
    if incoming != settings.admin_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin key inválida")
