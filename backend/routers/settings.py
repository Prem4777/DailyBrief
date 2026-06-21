"""
routers/settings.py — User service connection settings endpoints.

Routes:
  GET    /api/settings/services              — check connection status for each service
  POST   /api/settings/notion-token          — save a Notion integration token
  DELETE /api/settings/services/{service}    — disconnect a service
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models.credential import UserCredential
from models.user import User
from services.credential_service import encrypt_token_data

router = APIRouter()

_SUPPORTED_SERVICES = {"gmail", "gcal", "notion"}


class ServiceStatusResponse(BaseModel):
    """Response body for GET /api/settings/services."""

    gmail: bool = False
    gcal: bool = False
    notion: bool = False


class NotionTokenRequest(BaseModel):
    """Request body for POST /api/settings/notion-token."""

    access_token: str
    database_id: str


@router.get(
    "/settings/services",
    response_model=ServiceStatusResponse,
    summary="Check which external services are connected",
)
async def get_service_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ServiceStatusResponse:
    """Return the connection status for Gmail, GCal, and Notion.

    A service is considered "connected" if a UserCredential row exists for it.

    TODO: also check whether the stored token is still valid (not expired).
    """
    result = await db.execute(
        select(UserCredential.service).where(
            UserCredential.user_id == current_user.id
        )
    )
    connected_services = set(result.scalars().all())

    return ServiceStatusResponse(
        gmail="gmail" in connected_services,
        gcal="gcal" in connected_services,
        notion="notion" in connected_services,
    )


@router.post("/settings/notion-token", summary="Save a Notion integration token")
async def save_notion_token(
    body: NotionTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    encrypted = encrypt_token_data({
        "access_token": body.access_token,
        "database_id": body.database_id,
    })
    result = await db.execute(
        select(UserCredential).where(
            UserCredential.user_id == current_user.id,
            UserCredential.service == "notion",
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.token_data = encrypted
    else:
        db.add(UserCredential(
            user_id=current_user.id,
            service="notion",
            token_data=encrypted,
        ))
    await db.flush()
    return Response(status_code=204)


@router.delete("/settings/services/{service}", summary="Disconnect a service")
async def disconnect_service(
    service: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    if service not in _SUPPORTED_SERVICES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown service '{service}'. Must be one of: {_SUPPORTED_SERVICES}",
        )
    await db.execute(
        delete(UserCredential).where(
            UserCredential.user_id == current_user.id,
            UserCredential.service == service,
        )
    )
    return Response(status_code=204)
