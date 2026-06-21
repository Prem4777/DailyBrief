"""
main.py — FastAPI application entry point.

Registers all routers, configures CORS, sets up the startup lifecycle
event, and exposes a /health check endpoint.

Run with:
    uvicorn main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import init_db

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Credential validation
# ---------------------------------------------------------------------------

def _validate_credentials() -> None:
    """Check that all required env vars are set. Exit with a clear message if not."""
    required: dict[str, str] = {
        "GOOGLE_CLIENT_ID": settings.google_client_id,
        "GOOGLE_CLIENT_SECRET": settings.google_client_secret,
        "JWT_SECRET_KEY": settings.jwt_secret_key,
        "CREDENTIAL_ENCRYPTION_KEY": settings.credential_encryption_key,
    }

    # JWT_SECRET_KEY has a default placeholder — treat it as unset
    if settings.jwt_secret_key == "change-me-in-production":
        required["JWT_SECRET_KEY"] = ""

    missing = [name for name, value in required.items() if not value]

    if missing:
        msg = (
            "\n"
            "╔══════════════════════════════════════════════════════╗\n"
            "║          DailyBrief — Missing credentials            ║\n"
            "╠══════════════════════════════════════════════════════╣\n"
        )
        for var in missing:
            msg += f"║  ✗  {var:<48}║\n"
        msg += (
            "╠══════════════════════════════════════════════════════╣\n"
            "║  Copy backend/.env.example → backend/.env and fill  ║\n"
            "║  in the missing values, then restart the server.    ║\n"
            "╚══════════════════════════════════════════════════════╝\n"
        )
        logger.critical(msg)
        sys.exit(1)

# ---------------------------------------------------------------------------
# Router imports
# ---------------------------------------------------------------------------
from routers import (
    actions_router,
    auth_router,
    briefing_router,
    chat_router,
    oauth_router,
    settings_router,
)

# Validate credentials at import time so the server refuses to start with
# a clear error rather than silently returning 401/500 on every request.
_validate_credentials()


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks before serving, teardown tasks on shutdown."""
    await init_db()
    yield


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="DailyBrief API",
    description="Backend for the DailyBrief AI-powered morning briefing app.",
    version="0.1.0",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(auth_router, tags=["auth"])
app.include_router(oauth_router, tags=["oauth"])
app.include_router(briefing_router, prefix="/api", tags=["briefing"])
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(actions_router, prefix="/api", tags=["actions"])
app.include_router(settings_router, prefix="/api", tags=["settings"])


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"])
async def health_check() -> dict[str, str]:
    """Simple liveness probe — returns 200 OK with status info."""
    return {"status": "ok", "service": "dailybrief-api"}
