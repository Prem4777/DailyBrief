"""
routers/auth.py — Authentication endpoints.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models.user import User
from schemas.auth import LoginRequest, SignupRequest, TokenResponse
from services.auth_service import create_access_token, hash_password, verify_password

router = APIRouter()


@router.post("/auth/signup", response_model=TokenResponse)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    # Check duplicate email
    result = await db.execute(select(User).where(User.email == body.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        id=str(uuid.uuid4()),
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    await db.flush()

    token = create_access_token({"sub": user.id})
    await db.commit()
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/auth/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    result = await db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": user.id})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/auth/logout")
async def logout(_current_user: User = Depends(get_current_user)) -> Response:
    return Response(status_code=204)
