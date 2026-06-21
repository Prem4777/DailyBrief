"""
database.py — Async SQLAlchemy setup using aiosqlite.

Provides:
  - `engine`             : async engine bound to DATABASE_URL
  - `AsyncSessionLocal`  : session factory
  - `Base`               : declarative base for all ORM models
  - `get_db()`           : FastAPI dependency that yields a DB session
  - `init_db()`          : creates all tables on startup
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from config import settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""
    pass


# ---------------------------------------------------------------------------
# Engine & session factory
# ---------------------------------------------------------------------------

engine = create_async_engine(
    settings.database_url,
    echo=False,          # Set True for SQL debug logging
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session and close it when the request is done.

    Usage in a route:
        async def my_route(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# ---------------------------------------------------------------------------
# Startup helper
# ---------------------------------------------------------------------------

async def init_db() -> None:
    """Create all tables defined via Base.metadata.

    Called once at application startup (see main.py lifespan event).
    """
    # Import models here to ensure they are registered on Base.metadata
    # before create_all is called.
    import models  # noqa: F401 — side-effect import registers ORM models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
