"""
pipeline/stages/stage6_persist.py — Persist the completed briefing to the database.

Converts the Briefing schema object to a BriefingRecord ORM model and saves it.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from models.briefing import BriefingRecord
from schemas.briefing import Briefing

logger = logging.getLogger(__name__)


async def persist_briefing(
    db: AsyncSession,
    briefing: Briefing,
) -> BriefingRecord:
    """Persist a Briefing to the database as a BriefingRecord.

    Serialises the full Briefing to JSON for later retrieval, and also
    writes de-normalised stat fields so history list queries don't need to
    deserialise the full JSON.

    Args:
        db:       Active async database session.
        briefing: The completed Briefing to persist.

    Returns:
        The committed BriefingRecord ORM instance.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: if the DB write fails.
    """
    logger.debug(
        "Stage 6 — persisting briefing for user %s on %s",
        briefing.user_id,
        briefing.date,
    )

    # Serialise the full briefing JSON
    # TODO: use model.model_dump_json() with custom datetime serialiser if needed
    full_json = briefing.model_dump_json()

    record = BriefingRecord(
        user_id=briefing.user_id,
        date=briefing.date,
        generated_at=briefing.generated_at,
        focus_suggestion=briefing.focus_suggestion,
        urgent_email_count=briefing.urgent_email_count,
        meeting_count=briefing.meeting_count,
        overdue_task_count=briefing.overdue_task_count,
        calendar_conflict_flag=briefing.calendar_conflict_flag,
        partial=briefing.partial,
        unavailable_sources=json.dumps(briefing.unavailable_sources),
        full_briefing_json=full_json,
    )

    db.add(record)
    await db.flush()  # flush to get the auto-generated id before commit
    # Write the DB-generated id back onto the Briefing so callers have it
    briefing.id = record.id
    logger.debug("Stage 6 — persisted BriefingRecord id=%s", record.id)
    return record
