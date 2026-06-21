"""
pipeline/stages/stage3_crossref.py — Cross-reference emails, events, and tasks.

Delegates to CoordinatorAgent.cross_reference() which uses Gemini to find
semantic connections across data sources.
"""

from __future__ import annotations

import logging

from agents.coordinator_agent import CoordinatorAgent
from pipeline.stages.stage2_analyze import AnalysisResult
from schemas.briefing import CrossReference

logger = logging.getLogger(__name__)


async def cross_reference(
    coordinator: CoordinatorAgent,
    analysis_result: AnalysisResult,
) -> list[CrossReference]:
    """Find semantic connections across emails, events, and tasks.

    Args:
        coordinator:     Configured CoordinatorAgent.
        analysis_result: Typed data from stage 2.

    Returns:
        A list of CrossReference objects (may be empty).
    """
    logger.debug(
        "Stage 3 — cross-referencing %d emails, %d events, %d tasks",
        len(analysis_result.emails),
        len(analysis_result.events),
        len(analysis_result.tasks),
    )

    try:
        cross_refs = await coordinator.cross_reference(
            emails=analysis_result.emails,
            events=analysis_result.events,
            tasks=analysis_result.tasks,
        )
        logger.debug("Stage 3 — found %d cross-references", len(cross_refs))
        return cross_refs
    except Exception as exc:
        # Cross-referencing is non-critical — log and continue with empty list
        logger.warning("Stage 3 — cross-reference failed: %s", exc)
        return []
