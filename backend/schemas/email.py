"""
schemas/email.py — Pydantic models for classified email data.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ClassifiedEmail(BaseModel):
    """A Gmail message enriched with an AI-generated urgency classification."""

    id: str = Field(..., description="Gmail message ID.")
    subject: str
    sender: str = Field(..., description="Display name of the sender.")
    sender_email: str = Field(..., description="Raw email address of the sender.")
    snippet: str = Field(..., description="Short preview of the message body.")
    received_at: datetime = Field(..., description="UTC time the message was received.")

    classification: Literal["urgent", "can_wait", "fyi"] = Field(
        ...,
        description=(
            "'urgent' — requires action today; "
            "'can_wait' — non-urgent but relevant; "
            "'fyi' — informational only."
        ),
    )
    classification_reason: str = Field(
        ...,
        description="One-sentence explanation of why this classification was chosen.",
    )

    thread_id: str = Field(..., description="Gmail thread ID for grouping.")
