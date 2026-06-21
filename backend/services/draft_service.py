"""
services/draft_service.py — Generates draft email replies using Gemini.
"""

from __future__ import annotations

from schemas.email import ClassifiedEmail
from services.gemini_service import GeminiService

# Prompt template — adjust tone/length guidance as needed
_DRAFT_PROMPT_TEMPLATE = """
You are a professional email assistant. Draft a concise, professional reply to
the email below. Keep the reply to 3–5 sentences unless more detail is needed.

--- ORIGINAL EMAIL ---
From: {sender} <{sender_email}>
Subject: {subject}
Received: {received_at}

{snippet}

--- ADDITIONAL CONTEXT ---
{context}

--- INSTRUCTIONS ---
Write only the body of the reply. Do not include "Subject:", greetings
("Hi X,"), or sign-offs ("Best regards,") — the UI will add those.
"""


class DraftService:
    """Generates draft email replies using the Gemini LLM.

    Args:
        gemini: A configured GeminiService instance (injected dependency).
    """

    def __init__(self, gemini: GeminiService) -> None:
        self._gemini = gemini

    async def generate_draft(
        self,
        email: ClassifiedEmail,
        context: str = "",
    ) -> str:
        """Generate a draft reply for a classified email.

        Args:
            email:   The classified email to reply to.
            context: Optional extra context to include in the prompt (e.g.
                     related calendar events or tasks that the assistant
                     found via cross-referencing).

        Returns:
            A plain-text draft reply body.
        """
        # TODO: pull full email body from Gmail MCP instead of just the snippet
        prompt = _DRAFT_PROMPT_TEMPLATE.format(
            sender=email.sender,
            sender_email=email.sender_email,
            subject=email.subject,
            received_at=email.received_at.isoformat(),
            snippet=email.snippet,
            context=context or "No additional context.",
        )

        draft = await self._gemini.generate(prompt)
        return draft.strip()
