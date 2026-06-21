"""
schemas/__init__.py — Re-exports all Pydantic schemas for convenient imports.
"""

from schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from schemas.briefing import (
    Briefing,
    BriefingHistoryItem,
    CrossReference,
)
from schemas.calendar import (
    CalendarEvent,
    CalendarProposal,
    EventCreate,
    FreeSlot,
)
from schemas.chat import ChatMessage, ChatRequest, ChatResponse
from schemas.email import ClassifiedEmail
from schemas.tasks import ClassifiedTask

__all__ = [
    # auth
    "SignupRequest",
    "LoginRequest",
    "TokenResponse",
    "UserResponse",
    # email
    "ClassifiedEmail",
    # calendar
    "CalendarEvent",
    "FreeSlot",
    "CalendarProposal",
    "EventCreate",
    # tasks
    "ClassifiedTask",
    # briefing
    "Briefing",
    "CrossReference",
    "BriefingHistoryItem",
    # chat
    "ChatMessage",
    "ChatRequest",
    "ChatResponse",
]
