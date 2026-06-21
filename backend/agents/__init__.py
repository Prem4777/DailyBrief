"""
agents/__init__.py — Exports all agent classes.
"""

from agents.base_agent import BaseAgent
from agents.calendar_agent import CalendarAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.email_agent import EmailAgent
from agents.notes_agent import NotesAgent

__all__ = [
    "BaseAgent",
    "EmailAgent",
    "CalendarAgent",
    "NotesAgent",
    "CoordinatorAgent",
]
