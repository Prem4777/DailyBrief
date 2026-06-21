"""
models/briefing.py — SQLAlchemy ORM model for persisted briefing records.

Table: briefing_records
Stores a de-normalised snapshot of each generated briefing so users can
retrieve history without hitting external APIs again.

Heavy nested data (emails, events, tasks) is stored as JSON text in
`full_briefing_json` and re-hydrated at read time.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class BriefingRecord(Base):
    """Persisted briefing snapshot for a user on a given date."""

    __tablename__ = "briefing_records"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date: Mapped[date] = mapped_column(Date, nullable=False)
    """The calendar date this briefing covers (e.g. 2025-06-12)."""

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # --- Summary stats (for history list view without deserialising full JSON) ---

    summary_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    focus_suggestion: Mapped[str | None] = mapped_column(Text, nullable=True)
    urgent_email_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    meeting_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    overdue_task_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    calendar_conflict_flag: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    """True if any calendar conflict was detected."""

    # --- Partial / degraded state ---

    partial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    """True if one or more data sources were unavailable during generation."""

    unavailable_sources: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    """JSON-encoded list[str] of source names that failed (e.g. ["gmail"])."""

    # --- Full payload ---

    full_briefing_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    """JSON-serialised Briefing schema object. Used to re-hydrate full briefing."""

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User",
        back_populates="briefings",
    )

    def __repr__(self) -> str:
        return (
            f"<BriefingRecord id={self.id!r} user_id={self.user_id!r} "
            f"date={self.date!r}>"
        )
