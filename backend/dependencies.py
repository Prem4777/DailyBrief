"""
dependencies.py — Shared FastAPI dependencies.

Provides:
  - `get_current_user`: decodes JWT bearer token and returns the
    authenticated User ORM instance.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.user import User
from services.auth_service import decode_token

# The token URL is only used for the Swagger UI "Authorize" dialog;
# our actual login endpoint is /auth/login.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Decode the JWT bearer token and return the corresponding User row.

    Raises:
        HTTP 401 — if the token is missing, expired, or invalid.
        HTTP 401 — if the user referenced in the token no longer exists.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # TODO: call decode_token and extract the user_id ("sub") claim
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # TODO: fetch user from DB by user_id
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user
