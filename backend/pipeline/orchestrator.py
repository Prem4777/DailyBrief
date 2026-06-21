"""
pipeline/orchestrator.py — Top-level pipeline orchestrator.

Runs all 6 pipeline stages in order:
  1. Gather       — fetch raw data from Gmail, GCal, Notion
  2. Analyze      — classify and enrich each data type
  3. Cross-ref    — find connections across sources
  4. Synthesize   — build the full Briefing with AI focus suggestion
  5. Propose      — generate calendar action proposals
  6. Persist      — save to database

Also loads user credentials from the DB and instantiates MCP clients.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agents.calendar_agent import CalendarAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.email_agent import EmailAgent
from agents.notes_agent import NotesAgent
from mcp.gcal_client import GCalMCPClient
from mcp.gmail_client import GmailMCPClient
from mcp.notion_client import NotionMCPClient
from models.credential import UserCredential
from pipeline.session_store import session_store
from pipeline.stages.stage1_gather import gather_data
from pipeline.stages.stage2_analyze import analyze_data
from pipeline.stages.stage3_crossref import cross_reference
from pipeline.stages.stage4_synthesize import synthesize
from pipeline.stages.stage5_propose import propose_actions
from pipeline.stages.stage6_persist import persist_briefing
from schemas.briefing import Briefing
from services.credential_service import decrypt_token_data
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Coordinates the full morning briefing generation pipeline.

    Usage:
        orchestrator = PipelineOrchestrator()
        briefing = await orchestrator.run(user_id=user.id, db=db)
    """

    def __init__(self) -> None:
        # Lazily instantiated — GeminiService validates the API key on init
        self._gemini: GeminiService | None = None

    def _get_gemini(self) -> GeminiService:
        if self._gemini is None:
            self._gemini = GeminiService()
        return self._gemini

    async def _load_credentials(
        self, user_id: str, db: AsyncSession
    ) -> dict[str, dict]:
        """Load and decrypt all credentials for `user_id`.

        Args:
            user_id: The authenticated user's ID.
            db:      Active database session.

        Returns:
            A dict mapping service name → decrypted token dict.
            e.g. {"gmail": {...}, "gcal": {...}, "notion": {...}}
        """
        result = await db.execute(
            select(UserCredential).where(UserCredential.user_id == user_id)
        )
        credentials_rows = result.scalars().all()

        creds: dict[str, dict] = {}
        for row in credentials_rows:
            try:
                creds[row.service] = decrypt_token_data(row.token_data)
            except Exception as exc:
                logger.warning(
                    "Failed to decrypt credentials for service '%s': %s",
                    row.service,
                    exc,
                )
        return creds

    async def run(self, user_id: str, db: AsyncSession) -> Briefing:
        """Execute the full briefing pipeline for `user_id`.

        Args:
            user_id: The authenticated user's ID.
            db:      Active async database session.

        Returns:
            The completed Briefing, also stored in the session store.

        Raises:
            RuntimeError: If synthesis (stage 4) fails entirely.
        """
        today = datetime.now(timezone.utc).date()
        logger.info("Pipeline starting for user %s on %s", user_id, today)

        # --- Load credentials & instantiate MCP clients ---
        creds = await self._load_credentials(user_id, db)

        gmail_client = GmailMCPClient(credentials=creds.get("gmail", {}))
        gcal_client = GCalMCPClient(credentials=creds.get("gcal", {}))
        notion_client = NotionMCPClient(credentials=creds.get("notion", {}))

        # --- Instantiate agents ---
        gemini = self._get_gemini()
        email_agent = EmailAgent(gemini)
        calendar_agent = CalendarAgent(gemini)
        notes_agent = NotesAgent(gemini)
        coordinator = CoordinatorAgent(gemini)

        # Load notion_db_id from user credentials
        notion_db_id = creds.get("notion", {}).get("database_id", "")

        # --- Stage 1: Gather ---
        gather_result = await gather_data(
            email_agent=email_agent,
            calendar_agent=calendar_agent,
            notes_agent=notes_agent,
            gmail_client=gmail_client,
            gcal_client=gcal_client,
            notion_client=notion_client,
            date=today,
            notion_db_id=notion_db_id,
        )

        # --- Stage 2: Analyze ---
        analysis_result = await analyze_data(
            email_agent=email_agent,
            calendar_agent=calendar_agent,
            notes_agent=notes_agent,
            gather_result=gather_result,
            today=today,
        )

        # --- Stage 3: Cross-reference ---
        cross_refs = await cross_reference(coordinator, analysis_result)

        # --- Stage 4: Synthesize ---
        briefing = await synthesize(
            coordinator=coordinator,
            analysis_result=analysis_result,
            cross_refs=cross_refs,
            user_id=user_id,
            date=today,
        )

        # Mark as partial if any sources were unavailable
        if gather_result.unavailable_sources:
            briefing.partial = True
            briefing.unavailable_sources = gather_result.unavailable_sources

        proposals = propose_actions(coordinator, briefing)
        briefing.proposals = proposals

        # --- Stage 6: Persist ---
        await persist_briefing(db, briefing)

        # --- Store in session ---
        session_store.set(user_id, briefing, proposals)

        logger.info("Pipeline complete for user %s", user_id)
        return briefing
