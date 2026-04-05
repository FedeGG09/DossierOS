from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.core.config import settings
from app.middleware.auth import add_supabase_auth_middleware

app = FastAPI(title=settings.app_name, debug=settings.debug, version="1.0.0")

add_supabase_auth_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": str(exc) if settings.debug else "Unexpected error",
        },
    )

app.include_router(router)

@app.get("/", tags=["health"])
def root():
    return {
        "service": settings.app_name,
        "status": "running",
        "version": "1.0.0",
    }

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}