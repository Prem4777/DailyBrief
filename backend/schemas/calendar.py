"""
schemas/calendar.py — Pydantic models for calendar events, free slots,
proposals, and event creation payloads.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    """A Google Calendar event enriched with conflict / back-to-back metadata."""

    id: str = Field(..., description="Google Calendar event ID.")
    title: str
    start: datetime
    end: datetime
    attendees: list[str] = Field(default_factory=list, description="List of attendee emails.")
    description: str | None = None
    location: str | None = None

    conflict_flag: bool = Field(
        default=False,
        description="True if this event overlaps with another event.",
    )
    back_to_back_flag: bool = Field(
        default=False,
        description="True if this event starts immediately after another event ends.",
    )
    conflict_with_id: str | None = Field(
        default=None,
        description="ID of the conflicting event, if conflict_flag is True.",
    )


class FreeSlot(BaseModel):
    """A contiguous window of free time on the calendar."""

    start: datetime
    end: datetime
    duration_minutes: int = Field(..., description="Length of the slot in minutes.")


class CalendarProposal(BaseModel):
    """An AI-generated suggestion to schedule a task in a free calendar slot."""

    task_id: str = Field(..., description="ID of the Notion/task item to schedule.")
    task_title: str
    proposed_start: datetime
    proposed_end: datetime
    rationale: str = Field(
        ...,
        description="Explanation of why this slot was chosen for this task.",
    )


class EventCreate(BaseModel):
    """Payload used to create a new Google Calendar event."""

    title: str
    start: datetime
    end: datetime
    description: str | None = None
