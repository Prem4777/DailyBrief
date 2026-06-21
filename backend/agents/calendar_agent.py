"""
agents/calendar_agent.py — Fetches GCal events and detects conflicts/free slots.
Fully deterministic — no LLM.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone

from agents.base_agent import BaseAgent
from mcp.gcal_client import GCalMCPClient
from schemas.calendar import CalendarEvent, FreeSlot
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

_BACK_TO_BACK_SECS = 300   # 5 minutes
_MIN_FREE_SLOT_MINS = 30
_WORKDAY_START = 9
_WORKDAY_END = 18


def _parse_dt(s: str | None) -> datetime | None:
    if not s:
        return None
    try:
        # Handle Z suffix and offset-aware strings
        s = s.replace("Z", "+00:00")
        return datetime.fromisoformat(s)
    except Exception:
        return None


class CalendarAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService) -> None:
        super().__init__(gemini_service)

    async def fetch(self, gcal_client: GCalMCPClient, date: date) -> list[dict]:
        return await gcal_client.fetch_today_events(date)

    async def analyze(self, raw_events: list[dict]) -> tuple[list[CalendarEvent], list[FreeSlot]]:
        if not raw_events:
            return [], []

        events: list[CalendarEvent] = []
        for raw in raw_events:
            try:
                ev = self._parse_event(raw)
                if ev:
                    events.append(ev)
            except Exception as exc:
                logger.warning("Failed to parse event %s: %s", raw.get("id"), exc)

        # Sort by start time
        events.sort(key=lambda e: e.start)

        # Detect conflicts and back-to-back
        for i, ev in enumerate(events):
            for j in range(i + 1, len(events)):
                other = events[j]
                if other.start >= ev.end:
                    break
                # Overlap
                if other.start < ev.end:
                    ev.conflict_flag = True
                    other.conflict_flag = True
                    ev.conflict_with_id = other.id
                    other.conflict_with_id = ev.id

            # Back-to-back: check next event
            if i + 1 < len(events):
                nxt = events[i + 1]
                gap = (nxt.start - ev.end).total_seconds()
                if 0 <= gap <= _BACK_TO_BACK_SECS:
                    ev.back_to_back_flag = True
                    nxt.back_to_back_flag = True

        free_slots = self._find_free_slots(events, date if isinstance(date, type(date)) else events[0].start.date() if events else datetime.now().date())

        return events, free_slots

    def _parse_event(self, raw: dict) -> CalendarEvent | None:
        start_info = raw.get("start", {})
        end_info = raw.get("end", {})

        # Handle all-day events (date only, no dateTime)
        start_str = start_info.get("dateTime") or start_info.get("date")
        end_str = end_info.get("dateTime") or end_info.get("date")

        if not start_str or not end_str:
            return None

        start = _parse_dt(start_str)
        end = _parse_dt(end_str)

        if not start or not end:
            return None

        # Make timezone-aware if naive
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)

        attendees = [
            a.get("email", "") for a in raw.get("attendees", [])
            if a.get("email")
        ]

        return CalendarEvent(
            id=raw.get("id", ""),
            title=raw.get("summary", "(No title)"),
            start=start,
            end=end,
            attendees=attendees,
            description=raw.get("description") or "",
            location=raw.get("location"),
            conflict_flag=False,
            back_to_back_flag=False,
            conflict_with_id=None,
        )

    def _find_free_slots(self, events: list[CalendarEvent], target_date: date) -> list[FreeSlot]:
        free = []
        tz = timezone.utc
        workday_start = datetime(target_date.year, target_date.month, target_date.day,
                                 _WORKDAY_START, 0, 0, tzinfo=tz)
        workday_end = datetime(target_date.year, target_date.month, target_date.day,
                               _WORKDAY_END, 0, 0, tzinfo=tz)

        # Only events within workday
        day_events = [e for e in events if e.end > workday_start and e.start < workday_end]

        cursor = workday_start
        for ev in day_events:
            slot_start = cursor
            slot_end = min(ev.start, workday_end)
            if slot_end > slot_start:
                mins = int((slot_end - slot_start).total_seconds() / 60)
                if mins >= _MIN_FREE_SLOT_MINS:
                    free.append(FreeSlot(start=slot_start, end=slot_end, duration_minutes=mins))
            cursor = max(cursor, ev.end)

        # Gap after last event
        if cursor < workday_end:
            mins = int((workday_end - cursor).total_seconds() / 60)
            if mins >= _MIN_FREE_SLOT_MINS:
                free.append(FreeSlot(start=cursor, end=workday_end, duration_minutes=mins))

        return free
