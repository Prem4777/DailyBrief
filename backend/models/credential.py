"""
models/credential.py — SQLAlchemy ORM model for stored OAuth / API credentials.

Table: user_credentials
  - id          : integer primary key
  - user_id     : FK → users.id
  - service     : one of 'gmail' | 'gcal' | 'notion'
  - token_data  : Fernet-encrypted JSON token blob
  - connected_at: UTC timestamp when the credential was saved

Unique constraint: (user_id, service) — one credential per service per user.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Literal

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

ServiceName = Literal["gmail", "gcal", "notion"]


class UserCredential(Base):
    """Stores encrypted OAuth tokens or API tokens for a connected service."""

    __tablename__ = "user_credentials"

    __table_args__ = (
        UniqueConstraint("user_id", "service", name="uq_user_service"),
    )

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

    service: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    """One of 'gmail', 'gcal', 'notion'."""

    token_data: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    """Fernet-encrypted JSON blob. Decrypt via credential_service before use."""

    connected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------

    user: Mapped["User"] = relationship(  # type: ignore[name-defined]
        "User",
        back_populates="credentials",
    )

    def __repr__(self) -> str:
        return (
            f"<UserCredential user_id={self.user_id!r} service={self.service!r}>"
        )
