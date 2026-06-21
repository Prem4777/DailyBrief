"""
pipeline/stages/stage4_synthesize.py — Synthesise a complete Briefing object.

Delegates to CoordinatorAgent.synthesize() which calls Gemini to generate
the focus suggestion and assembles all data into the Briefing schema.
"""

from __future__ import annotations

import logging
from datetime import date

from agents.coordinator_agent import CoordinatorAgent
from pipeline.stages.stage2_analyze import AnalysisResult
from schemas.briefing import Briefing, CrossReference

logger = logging.getLogger(__name__)


async def synthesize(
    coordinator: CoordinatorAgent,
    analysis_result: AnalysisResult,
    cross_refs: list[CrossReference],
    user_id: str,
    date: date,
) -> Briefing:
    """Synthesise all analysed data into a single Briefing object.

    Args:
        coordinator:     Configured CoordinatorAgent.
        analysis_result: Typed data from stage 2.
        cross_refs:      Cross-references from stage 3.
        user_id:         The authenticated user's ID.
        date:            The briefing date.

    Returns:
        A complete Briefing instance ready to be persisted and returned.

    Raises:
        Exception: Propagates any synthesis error up to the orchestrator.
    """
    logger.debug("Stage 4 — synthesising briefing for user %s on %s", user_id, date)

    briefing = await coordinator.synthesize(
        emails=analysis_result.emails,
        events=analysis_result.events,
        tasks=analysis_result.tasks,
        cross_refs=cross_refs,
        free_slots=analysis_result.free_slots,
        user_id=user_id,
        date=date,
    )

    logger.debug("Stage 4 — briefing synthesised: focus_suggestion set")
    return briefing
