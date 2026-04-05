from __future__ import annotations

from fastapi import FastAPI, Request

from app.core.security import extract_bearer_token, verify_supabase_jwt


def add_supabase_auth_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def supabase_auth_middleware(request: Request, call_next):
        request.state.supabase_token = None
        request.state.supabase_claims = None
        request.state.user_id = None
        request.state.user_email = None

        auth_header = request.headers.get("authorization")
        token = extract_bearer_token(auth_header)

        if token:
            claims = verify_supabase_jwt(token)
            request.state.supabase_token = token
            request.state.supabase_claims = claims
            request.state.user_id = claims.get("sub")
            request.state.user_email = claims.get("email")

        response = await call_next(request)
        return response
