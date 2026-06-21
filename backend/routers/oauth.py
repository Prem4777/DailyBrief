"""
routers/oauth.py — Google OAuth 2.0 endpoints.

Routes:
  GET /auth/google/start      — redirect user to Google consent screen
  GET /auth/google/callback   — exchange auth code for tokens, save credentials,
                                create or find the user, return a JWT

The flow works for both "Sign in with Google" (new + existing users) and
connecting Google services for an already-logged-in user.

State parameter encoding:
  "<user_id_or_NEW>:<random_nonce>"
  - If a JWT is present when /start is called, user_id is embedded so the
    callback links the tokens to the existing account.
  - If no JWT is present (sign-in flow), "NEW" is used; the callback creates
    or finds the account by Google email.
"""

from __future__ import annotations

import json
import secrets
import uuid
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings
from database import get_db
from dependencies import get_current_user
from models.credential import UserCredential
from models.user import User
from services.auth_service import create_access_token
from services.credential_service import encrypt_token_data

router = APIRouter()

# Google OAuth 2.0 endpoints
_GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

# Scopes for Gmail read + Google Calendar read/write + user identity
_OAUTH_SCOPES = [
    "openid",
    "email",
    "profile",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar",
]

# Frontend URL to redirect to after a successful OAuth callback
_FRONTEND_SUCCESS_URL = "http://localhost:5173/oauth/callback"
_FRONTEND_ERROR_URL = "http://localhost:5173/login?error=oauth_failed"


@router.get(
    "/auth/google/start",
    summary="Initiate Google OAuth flow",
    response_class=RedirectResponse,
)
async def google_oauth_start(
    # Optional: if the user is already logged in, embed their id in state
    # so the callback links tokens to the existing account.
    # We use a soft dependency — don't raise 401 if there's no token.
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Redirect the user to Google's consent screen."""
    # Use a random nonce as the state — we encode just a random value here
    # because this is also used as the "Sign in with Google" entry point
    # where no user is logged in yet.  The callback handles both cases.
    state = secrets.token_urlsafe(32)

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(_OAUTH_SCOPES),
        "access_type": "offline",   # request a refresh token
        "prompt": "consent",        # always show consent to get refresh token
        "state": state,
    }

    url = f"{_GOOGLE_AUTH_URL}?{urlencode(params)}"
    return RedirectResponse(url=url, status_code=302)


@router.get(
    "/auth/google/callback",
    summary="Handle Google OAuth callback",
)
async def google_oauth_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: str = Query(..., description="State parameter"),
    error: str | None = Query(None, description="Error from Google if user denied"),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Exchange the auth code for tokens, upsert the user, store credentials."""

    if error:
        return RedirectResponse(url=_FRONTEND_ERROR_URL, status_code=302)

    # ------------------------------------------------------------------
    # 1. Exchange authorization code for tokens
    # ------------------------------------------------------------------
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            _GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "redirect_uri": settings.google_redirect_uri,
                "grant_type": "authorization_code",
            },
        )

    if token_resp.status_code != 200:
        return RedirectResponse(url=_FRONTEND_ERROR_URL, status_code=302)

    token_data = token_resp.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not access_token:
        return RedirectResponse(url=_FRONTEND_ERROR_URL, status_code=302)

    # ------------------------------------------------------------------
    # 2. Fetch the user's Google profile (email)
    # ------------------------------------------------------------------
    async with httpx.AsyncClient() as client:
        userinfo_resp = await client.get(
            _GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if userinfo_resp.status_code != 200:
        return RedirectResponse(url=_FRONTEND_ERROR_URL, status_code=302)

    userinfo = userinfo_resp.json()
    google_email: str | None = userinfo.get("email")

    if not google_email:
        return RedirectResponse(url=_FRONTEND_ERROR_URL, status_code=302)

    # ------------------------------------------------------------------
    # 3. Find or create the DailyBrief user
    # ------------------------------------------------------------------
    result = await db.execute(select(User).where(User.email == google_email))
    user = result.scalar_one_or_none()

    if user is None:
        # New user — create account with no password (Google-only sign-in)
        user = User(
            id=str(uuid.uuid4()),
            email=google_email,
            password_hash="",   # empty — Google-authed users don't use passwords
        )
        db.add(user)
        await db.flush()

    # ------------------------------------------------------------------
    # 4. Store / update Gmail and GCal credentials (both share same tokens)
    # ------------------------------------------------------------------
    credential_blob = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_data.get("token_type", "Bearer"),
        "expires_in": token_data.get("expires_in"),
        "scope": token_data.get("scope", ""),
    }
    encrypted = encrypt_token_data(credential_blob)

    for service in ("gmail", "gcal"):
        result = await db.execute(
            select(UserCredential).where(
                UserCredential.user_id == user.id,
                UserCredential.service == service,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.token_data = encrypted
        else:
            db.add(UserCredential(
                id=str(uuid.uuid4()),
                user_id=user.id,
                service=service,
                token_data=encrypted,
            ))

    await db.commit()

    # ------------------------------------------------------------------
    # 5. Issue a DailyBrief JWT and redirect to the frontend
    # ------------------------------------------------------------------
    jwt = create_access_token({"sub": user.id})
    redirect_url = f"{_FRONTEND_SUCCESS_URL}?token={jwt}"
    return RedirectResponse(url=redirect_url, status_code=302)
