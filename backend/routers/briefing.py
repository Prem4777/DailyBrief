"""
routers/briefing.py — Briefing generation and history endpoints.

All routes require a valid JWT (via get_current_user dependency).

Routes:
  POST /api/briefing/run             — trigger a fresh briefing generation
  GET  /api/briefing/current         — return the active session briefing
  GET  /api/briefing/history         — list all past briefings for the user
  GET  /api/briefing/history/{id}    — retrieve a single past briefing by ID
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from dependencies import get_current_user
from models.briefing import BriefingRecord
from models.user import User
from pipeline.orchestrator import PipelineOrchestrator
from pipeline.session_store import session_store
from schemas.briefing import Briefing, BriefingHistoryItem

router = APIRouter()

# Singleton orchestrator — instantiated once per process
_orchestrator = PipelineOrchestrator()


@router.post(
    "/briefing/run",
    response_model=Briefing,
    summary="Generate a fresh morning briefing",
)
async def run_briefing(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Briefing:
    """Trigger the full 6-stage briefing pipeline for the current user.

    Returns the completed Briefing. Stores it in the in-memory session store
    so /current can return it without a DB round-trip.

    TODO: add concurrency guard (prevent two simultaneous runs per user).
    """
    try:
        briefing = await _orchestrator.run(user_id=current_user.id, db=db)
        return briefing
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Briefing generation failed: {exc}",
        )


@router.get(
    "/briefing/current",
    response_model=Briefing | None,
    summary="Return the active briefing from session",
)
async def get_current_briefing(
    current_user: User = Depends(get_current_user),
) -> Briefing | None:
    """Return the most recently generated briefing from the in-memory session.

    Returns null if no briefing has been generated in this session.
    """
    session = session_store.get(current_user.id)
    if session is None:
        return None
    return session.briefing


@router.get(
    "/briefing/history",
    response_model=list[BriefingHistoryItem],
    summary="List all past briefings for the current user",
)
async def get_briefing_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BriefingHistoryItem]:
    """Return a list of past briefing summaries, most recent first.

    TODO: add pagination (limit/offset) if history grows large.
    """
    result = await db.execute(
        select(BriefingRecord)
        .where(BriefingRecord.user_id == current_user.id)
        .order_by(BriefingRecord.generated_at.desc())
    )
    records = result.scalars().all()
    return [BriefingHistoryItem.model_validate(r) for r in records]


@router.get(
    "/briefing/history/{briefing_id}",
    response_model=Briefing,
    summary="Retrieve a single past briefing by ID",
)
async def get_briefing_by_id(
    briefing_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Briefing:
    """Deserialise and return a historical briefing by its ID.

    Ensures the briefing belongs to the current user (ownership check).
    """
    result = await db.execute(
        select(BriefingRecord).where(
            BriefingRecord.id == briefing_id,
            BriefingRecord.user_id == current_user.id,
        )
    )
    record = result.scalar_one_or_none()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Briefing not found",
        )

    if not record.full_briefing_json:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Briefing JSON is missing from the stored record",
        )

    # TODO: handle schema migration if Briefing model evolves
    return Briefing.model_validate_json(record.full_briefing_json)
