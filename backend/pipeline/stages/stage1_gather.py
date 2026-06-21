"""
pipeline/stages/stage1_gather.py — Gather raw data from all external sources.

Fetches from Gmail, Google Calendar, and Notion in parallel. Each source is
wrapped in a try/except so that one failing source does not abort the whole
pipeline. Failures are recorded in `unavailable_sources`.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import date

from agents.calendar_agent import CalendarAgent
from agents.email_agent import EmailAgent
from agents.notes_agent import NotesAgent
from mcp.gcal_client import GCalMCPClient
from mcp.gmail_client import GmailMCPClient
from mcp.notion_client import NotionMCPClient

logger = logging.getLogger(__name__)


@dataclass
class GatherResult:
    """Raw data collected from all available sources."""

    raw_emails: list[dict] = field(default_factory=list)
    raw_events: list[dict] = field(default_factory=list)
    raw_tasks: list[dict] = field(default_factory=list)
    unavailable_sources: list[str] = field(default_factory=list)
    """Names of sources that raised exceptions during fetch (e.g. ['gmail'])."""


async def gather_data(
    email_agent: EmailAgent,
    calendar_agent: CalendarAgent,
    notes_agent: NotesAgent,
    gmail_client: GmailMCPClient,
    gcal_client: GCalMCPClient,
    notion_client: NotionMCPClient,
    date: date,
    notion_db_id: str,
) -> GatherResult:
    """Fetch raw data from Gmail, GCal, and Notion concurrently.

    Each source is isolated: if it raises an exception the others continue.
    The caller can check `result.unavailable_sources` to decide whether the
    briefing should be flagged as partial.

    Args:
        email_agent:     Configured EmailAgent.
        calendar_agent:  Configured CalendarAgent.
        notes_agent:     Configured NotesAgent.
        gmail_client:    Authenticated GmailMCPClient.
        gcal_client:     Authenticated GCalMCPClient.
        notion_client:   Authenticated NotionMCPClient.
        date:            The briefing date.
        notion_db_id:    The Notion database ID from user settings.

    Returns:
        A GatherResult containing raw data lists and unavailable_sources.
    """
    result = GatherResult()

    async def _fetch_emails() -> None:
        try:
            result.raw_emails = await email_agent.fetch(gmail_client, date)
        except Exception as exc:
            logger.warning("Stage 1 — Gmail fetch failed: %s", exc)
            result.unavailable_sources.append("gmail")

    async def _fetch_events() -> None:
        try:
            result.raw_events = await calendar_agent.fetch(gcal_client, date)
        except Exception as exc:
            logger.warning("Stage 1 — GCal fetch failed: %s", exc)
            result.unavailable_sources.append("gcal")

    async def _fetch_tasks() -> None:
        try:
            result.raw_tasks = await notes_agent.fetch(notion_client, notion_db_id)
        except Exception as exc:
            logger.warning("Stage 1 — Notion fetch failed: %s", exc)
            result.unavailable_sources.append("notion")

    await asyncio.gather(
        _fetch_emails(),
        _fetch_events(),
        _fetch_tasks(),
    )

    return result
