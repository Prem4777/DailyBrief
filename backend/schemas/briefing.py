"""
schemas/briefing.py — Pydantic models for the full briefing payload
and history list items.
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field

from schemas.calendar import CalendarEvent, CalendarProposal, FreeSlot
from schemas.email import ClassifiedEmail
from schemas.tasks import ClassifiedTask


class CrossReference(BaseModel):
    """Links an email, calendar event, and/or task that are related to each other."""

    email_id: str | None = None
    event_id: str | None = None
    task_id: str | None = None
    relationship_description: str = Field(
        ...,
        description="Human-readable explanation of why these items are related.",
    )


class Briefing(BaseModel):
    """The full morning briefing payload returned to the frontend."""

    # Metadata
    id: str = Field(default="", description="Set by stage6_persist after DB insert.")
    user_id: str
    generated_at: datetime
    date: date

    # AI-generated summary
    focus_suggestion: str = Field(
        ...,
        description="One-paragraph AI recommendation for how to focus the day.",
    )

    # High-level stats
    urgent_email_count: int = 0
    meeting_count: int = 0
    overdue_task_count: int = 0
    calendar_conflict_flag: bool = False

    # Detailed data
    emails: list[ClassifiedEmail] = Field(default_factory=list)
    events: list[CalendarEvent] = Field(default_factory=list)
    free_slots: list[FreeSlot] = Field(default_factory=list)
    tasks: list[ClassifiedTask] = Field(default_factory=list)

    # AI enrichments
    cross_references: list[CrossReference] = Field(default_factory=list)
    proposals: list[CalendarProposal] = Field(default_factory=list)

    # Degraded / partial state
    partial: bool = Field(
        default=False,
        description="True if one or more data sources were unavailable.",
    )
    unavailable_sources: list[str] = Field(
        default_factory=list,
        description="Names of sources that failed (e.g. ['gmail', 'notion']).",
    )


class BriefingHistoryItem(BaseModel):
    """Lightweight summary for the briefing history list view."""

    id: str
    date: date
    generated_at: datetime
    focus_suggestion: str | None
    urgent_email_count: int
    meeting_count: int
    overdue_task_count: int
    calendar_conflict_flag: bool
    partial: bool

    model_config = {"from_attributes": True}
