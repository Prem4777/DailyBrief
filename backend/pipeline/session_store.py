"""
pipeline/session_store.py — In-memory session store for briefing data and chat history.

Sessions are keyed by user_id and expire after 24 hours.
This is a singleton — import `session_store` from this module.

NOTE: This is an in-process store. For multi-worker deployments, replace
with a Redis-backed store.
"""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from schemas.briefing import Briefing
from schemas.calendar import CalendarProposal
from schemas.chat import ChatMessage

_SESSION_TTL_HOURS = 24


@dataclass
class SessionData:
    """All state associated with one active user session."""

    user_id: str
    briefing: Briefing | None = None
    proposals: list[CalendarProposal] = field(default_factory=list)
    chat_history: list[ChatMessage] = field(default_factory=list)
    pending_action: CalendarProposal | None = None
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    last_accessed: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SessionStore:
    """Thread-safe in-memory session store with TTL expiry.

    Usage:
        from pipeline.session_store import session_store

        session_store.set(user_id, briefing, proposals)
        data = session_store.get(user_id)
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionData] = {}
        self._lock = threading.Lock()

    def _evict_expired(self) -> None:
        """Remove sessions older than _SESSION_TTL_HOURS.

        Called lazily on each write operation.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=_SESSION_TTL_HOURS)
        expired = [
            uid
            for uid, data in self._sessions.items()
            if data.last_accessed < cutoff
        ]
        for uid in expired:
            del self._sessions[uid]

    def _touch(self, session: SessionData) -> None:
        """Update the last_accessed timestamp to prevent premature eviction."""
        session.last_accessed = datetime.now(timezone.utc)

    def set(
        self,
        user_id: str,
        briefing: Briefing,
        proposals: list[CalendarProposal],
    ) -> None:
        """Create or overwrite the session for `user_id`.

        Args:
            user_id:   The authenticated user's ID.
            briefing:  The freshly generated Briefing object.
            proposals: The list of CalendarProposals for the session.
        """
        with self._lock:
            self._evict_expired()
            existing = self._sessions.get(user_id)
            if existing:
                existing.briefing = briefing
                existing.proposals = proposals
                self._touch(existing)
            else:
                self._sessions[user_id] = SessionData(
                    user_id=user_id,
                    briefing=briefing,
                    proposals=proposals,
                )

    def get(self, user_id: str) -> SessionData | None:
        """Retrieve the active session for `user_id`, or None if not found.

        Args:
            user_id: The authenticated user's ID.

        Returns:
            The SessionData, or None if the session doesn't exist or expired.
        """
        with self._lock:
            session = self._sessions.get(user_id)
            if session is None:
                return None
            cutoff = datetime.now(timezone.utc) - timedelta(hours=_SESSION_TTL_HOURS)
            if session.last_accessed < cutoff:
                del self._sessions[user_id]
                return None
            self._touch(session)
            return session

    def get_chat_history(self, user_id: str) -> list[ChatMessage]:
        """Return the chat history for `user_id` (empty list if no session).

        Args:
            user_id: The authenticated user's ID.
        """
        session = self.get(user_id)
        return session.chat_history if session else []

    def append_message(self, user_id: str, msg: ChatMessage) -> None:
        """Append a message to the chat history for `user_id`.

        Creates a minimal session if one doesn't exist yet.

        Args:
            user_id: The authenticated user's ID.
            msg:     The ChatMessage to append.
        """
        with self._lock:
            session = self._sessions.get(user_id)
            if session is None:
                # TODO: consider whether to disallow chat without a briefing
                session = SessionData(user_id=user_id)
                self._sessions[user_id] = session
            session.chat_history.append(msg)
            self._touch(session)

    def set_pending_action(
        self, user_id: str, proposal: CalendarProposal
    ) -> None:
        """Store a pending calendar action awaiting user confirmation.

        Args:
            user_id:  The authenticated user's ID.
            proposal: The proposal the assistant is asking the user to confirm.
        """
        with self._lock:
            session = self._sessions.get(user_id)
            if session:
                session.pending_action = proposal
                self._touch(session)

    def get_pending_action(self, user_id: str) -> CalendarProposal | None:
        """Retrieve the pending calendar action for `user_id`.

        Args:
            user_id: The authenticated user's ID.

        Returns:
            The pending CalendarProposal, or None.
        """
        session = self.get(user_id)
        return session.pending_action if session else None

    def clear_pending_action(self, user_id: str) -> None:
        """Clear the pending action after the user confirms or rejects it.

        Args:
            user_id: The authenticated user's ID.
        """
        with self._lock:
            session = self._sessions.get(user_id)
            if session:
                session.pending_action = None
                self._touch(session)


# Singleton instance
session_store = SessionStore()
