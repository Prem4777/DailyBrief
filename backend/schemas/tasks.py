"""
schemas/tasks.py — Pydantic models for classified Notion tasks.
"""

from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ClassifiedTask(BaseModel):
    """A Notion task enriched with a deterministic due-date classification."""

    id: str = Field(..., description="Notion page ID.")
    title: str
    due_date: date | None = Field(
        default=None,
        description="ISO date string. None means no due date is set.",
    )
    classification: Literal["overdue", "due_today", "due_later"] = Field(
        ...,
        description=(
            "'overdue' — due date is in the past; "
            "'due_today' — due date is today; "
            "'due_later' — due date is in the future or not set."
        ),
    )
    project: str | None = Field(
        default=None,
        description="Parent project name from Notion, if available.",
    )
    url: str = Field(..., description="Notion page URL for deep-linking.")
