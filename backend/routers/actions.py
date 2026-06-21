"""
routers/actions.py — Email draft and calendar action endpoints.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_user
from database import get_db
from models.user import User
from pipeline.session_store import session_store
from schemas.calendar import CalendarProposal
from services.draft_service import DraftService
from services.gemini_service import GeminiService

router = APIRouter()
logger = logging.getLogger(__name__)

_gemini: GeminiService | None = None
_draft_service: DraftService | None = None


def _get_draft_service() -> DraftService:
    global _gemini, _draft_service
    if _gemini is None:
        _gemini = GeminiService()
    if _draft_service is None:
        _draft_service = DraftService(_gemini)
    return _draft_service


@router.post("/actions/draft")
async def generate_draft(
    email_id: str,
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    """Generate a draft reply for the given email ID."""
    session = session_store.get(current_user.id)
    if not session or not session.briefing:
        raise HTTPException(status_code=404, detail="No active briefing session")

    email = next((e for e in session.briefing.emails if e.id == email_id), None)
    if not email:
        raise HTTPException(status_code=404, detail="Email not found in current briefing")

    # Find any cross-reference context for this email
    context_parts = []
    for ref in session.briefing.cross_references:
        if ref.email_id == email_id:
            context_parts.append(ref.relationship_description)

    try:
        svc = _get_draft_service()
        draft = await svc.generate_draft(email, context="\n".join(context_parts))
        return {"draft": draft}
    except Exception as exc:
        logger.error("Draft generation failed: %s", exc)
        raise HTTPException(status_code=500, detail="Draft generation failed")


@router.post("/actions/calendar/propose", response_model=CalendarProposal)
async def propose_calendar_slot(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> CalendarProposal:
    """Propose a time slot for a task from the current briefing."""
    session = session_store.get(current_user.id)
    if not session or not session.briefing:
        raise HTTPException(status_code=404, detail="No active briefing session")

    task = next((t for t in session.briefing.tasks if t.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found in current briefing")

    # Find an existing proposal for this task
    proposal = next(
        (p for p in session.briefing.proposals if p.task_id == task_id), None
    )
    if not proposal:
        raise HTTPException(
            status_code=400,
            detail="No free slot available for this task",
        )

    session_store.set_pending_action(current_user.id, proposal)
    return proposal


@router.post("/actions/calendar/confirm")
async def confirm_calendar_action(
    proposal: CalendarProposal,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Confirm and write a proposed calendar event to Google Calendar."""
    from sqlalchemy import select
    from models.credential import UserCredential
    from services.credential_service import decrypt_token_data
    from mcp.gcal_client import GCalMCPClient
    from schemas.calendar import EventCreate

    result = await db.execute(
        select(UserCredential).where(
            UserCredential.user_id == current_user.id,
            UserCredential.service == "gcal",
        )
    )
    cred_row = result.scalar_one_or_none()

    if not cred_row:
        raise HTTPException(status_code=400, detail="Google Calendar not connected")

    try:
        creds = decrypt_token_data(cred_row.token_data)
        gcal = GCalMCPClient(credentials=creds)
        event = EventCreate(
            title=proposal.task_title,
            start=proposal.proposed_start,
            end=proposal.proposed_end,
            description=f"Scheduled by DailyBrief. {proposal.rationale}",
        )
        event_id = await gcal.create_event(event)
        session_store.clear_pending_action(current_user.id)
        return {"event_id": event_id}
    except Exception as exc:
        logger.error("Calendar confirm failed: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
