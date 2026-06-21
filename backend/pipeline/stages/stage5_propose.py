"""
pipeline/stages/stage5_propose.py — Generate calendar action proposals.

Delegates to CoordinatorAgent.propose_actions() which matches high-priority
tasks to available free calendar slots.
"""

from __future__ import annotations

import logging

from agents.coordinator_agent import CoordinatorAgent
from schemas.briefing import Briefing
from schemas.calendar import CalendarProposal

logger = logging.getLogger(__name__)


def propose_actions(
    coordinator: CoordinatorAgent,
    briefing: Briefing,
) -> list[CalendarProposal]:
    """Generate CalendarProposal suggestions from the synthesised Briefing.

    This stage is synchronous — proposal generation is a deterministic
    matching algorithm with no I/O.

    Args:
        coordinator: Configured CoordinatorAgent.
        briefing:    The synthesised Briefing from stage 4.

    Returns:
        A list of CalendarProposal suggestions (may be empty).
    """
    logger.debug("Stage 5 — generating action proposals")

    proposals = coordinator.propose_actions(
        briefing=briefing,
        free_slots=briefing.free_slots,
    )

    logger.debug("Stage 5 — generated %d proposals", len(proposals))
    return proposals
