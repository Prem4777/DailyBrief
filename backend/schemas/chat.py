"""
schemas/chat.py — Pydantic models for the chat API.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from schemas.calendar import CalendarProposal


class ChatMessage(BaseModel):
    """A single message in the chat history."""

    role: Literal["user", "assistant"] = Field(
        ..., description="'user' for human messages, 'assistant' for AI replies."
    )
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request body for POST /api/chat."""

    message: str = Field(..., min_length=1, description="The user's chat message.")


class ChatResponse(BaseModel):
    """Response from the chat endpoint."""

    message: ChatMessage = Field(..., description="The assistant's reply.")
    pending_action: CalendarProposal | None = Field(
        default=None,
        description=(
            "If the assistant is proposing a calendar action, this contains "
            "the proposal details for the user to confirm or reject."
        ),
    )
