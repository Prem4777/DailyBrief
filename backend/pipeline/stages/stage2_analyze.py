"""
pipeline/stages/stage2_analyze.py — Analyse raw data from all agents in parallel.

Calls EmailAgent.analyze(), CalendarAgent.analyze(), and NotesAgent.analyze()
concurrently. Uses the GatherResult from stage 1 as input.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import date

from agents.calendar_agent import CalendarAgent
from agents.email_agent import EmailAgent
from agents.notes_agent import NotesAgent
from pipeline.stages.stage1_gather import GatherResult
from schemas.calendar import CalendarEvent, FreeSlot
from schemas.email import ClassifiedEmail
from schemas.tasks import ClassifiedTask

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Typed, enriched data from all agents after analysis."""

    emails: list[ClassifiedEmail] = field(default_factory=list)
    events: list[CalendarEvent] = field(default_factory=list)
    free_slots: list[FreeSlot] = field(default_factory=list)
    tasks: list[ClassifiedTask] = field(default_factory=list)


async def analyze_data(
    email_agent: EmailAgent,
    calendar_agent: CalendarAgent,
    notes_agent: NotesAgent,
    gather_result: GatherResult,
    today: date,
) -> AnalysisResult:
    """Run all three agent analysis steps concurrently.

    Args:
        email_agent:    Configured EmailAgent.
        calendar_agent: Configured CalendarAgent.
        notes_agent:    Configured NotesAgent.
        gather_result:  Raw data from stage 1.
        today:          Reference date for task classification.

    Returns:
        An AnalysisResult with fully typed, enriched data.
    """
    result = AnalysisResult()

    async def _analyze_emails() -> None:
        try:
            result.emails = await email_agent.analyze(gather_result.raw_emails)
        except Exception as exc:
            logger.warning("Stage 2 — email analysis failed: %s", exc)
            result.emails = []

    async def _analyze_events() -> None:
        try:
            events, free_slots = await calendar_agent.analyze(gather_result.raw_events)
            result.events = events
            result.free_slots = free_slots
        except Exception as exc:
            logger.warning("Stage 2 — calendar analysis failed: %s", exc)
            result.events = []
            result.free_slots = []

    async def _analyze_tasks() -> None:
        try:
            result.tasks = await notes_agent.analyze(gather_result.raw_tasks, today)
        except Exception as exc:
            logger.warning("Stage 2 — task analysis failed: %s", exc)
            result.tasks = []

    await asyncio.gather(
        _analyze_emails(),
        _analyze_events(),
        _analyze_tasks(),
    )

    return result
