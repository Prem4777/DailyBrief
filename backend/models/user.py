"""
models/user.py — SQLAlchemy ORM model for application users.

Table: users
  - id           : UUID string, primary key
  - email        : unique user email address
  - password_hash: bcrypt hash of the user's password
  - created_at   : UTC timestamp of account creation
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    """Represents a registered DailyBrief user."""

    __tablename__ = "users"

    # Primary key — stored as a string UUID so SQLite plays nicely
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ---------------------------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------------------------

    credentials: Mapped[list["UserCredential"]] = relationship(  # type: ignore[name-defined]
        "UserCredential",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    briefings: Mapped[list["BriefingRecord"]] = relationship(  # type: ignore[name-defined]
        "BriefingRecord",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="BriefingRecord.generated_at.desc()",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!r} email={self.email!r}>"
