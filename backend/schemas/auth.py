"""
schemas/auth.py — Pydantic models for authentication endpoints.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SignupRequest(BaseModel):
    email: str = Field(..., description="User's email address.")
    password: str = Field(..., min_length=8, description="Plain-text password (min 8 chars).")


class LoginRequest(BaseModel):
    email: str = Field(..., description="User's email address.")
    password: str = Field(..., description="Plain-text password.")


class TokenResponse(BaseModel):
    """Response returned after a successful login or signup."""

    access_token: str = Field(..., description="JWT bearer token.")
    token_type: str = Field(default="bearer")


class UserResponse(BaseModel):
    """Public representation of a user — safe to return in API responses."""

    id: str = Field(..., description="UUID string.")
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
