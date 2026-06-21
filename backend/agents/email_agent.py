"""
agents/email_agent.py — Fetches Gmail messages and classifies them with Gemini.
"""

from __future__ import annotations

import json
import logging
from datetime import date

from agents.base_agent import BaseAgent
from mcp.gmail_client import GmailMCPClient
from schemas.email import ClassifiedEmail
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)

_BATCH_SIZE = 20

_PROMPT = """
Classify each email as "urgent", "can_wait", or "fyi".

Definitions:
  - urgent   : Requires action TODAY (reply, approval, decision, deadline)
  - can_wait : Relevant but not time-sensitive; can wait a few days
  - fyi      : Informational only — newsletters, notifications, receipts, CC

Return ONLY a valid JSON array. No markdown, no explanation.
Each element: {{"id": "<id>", "classification": "urgent"|"can_wait"|"fyi", "classification_reason": "<one sentence>"}}

Emails:
{emails_json}
"""


def _extract_header(headers: list[dict], name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _parse_raw_email(raw: dict) -> dict:
    """Normalize a Gmail API message into a flat dict."""
    payload = raw.get("payload", {})
    headers = payload.get("headers", [])
    return {
        "id": raw.get("id", ""),
        "thread_id": raw.get("threadId", ""),
        "subject": _extract_header(headers, "Subject") or "(no subject)",
        "from": _extract_header(headers, "From") or "",
        "snippet": raw.get("snippet", ""),
        "received_at": raw.get("internalDate", "0"),
    }


class EmailAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService) -> None:
        super().__init__(gemini_service)

    async def fetch(self, gmail_client: GmailMCPClient, date: date) -> list[dict]:
        return await gmail_client.fetch_today_emails(date)

    async def analyze(self, raw_emails: list[dict]) -> list[ClassifiedEmail]:
        if not raw_emails:
            return []

        parsed = [_parse_raw_email(e) for e in raw_emails]
        classified: list[ClassifiedEmail] = []

        # Process in batches
        for i in range(0, len(parsed), _BATCH_SIZE):
            batch = parsed[i:i + _BATCH_SIZE]
            slim = [{"id": e["id"], "subject": e["subject"],
                     "from": e["from"], "snippet": e["snippet"]} for e in batch]

            prompt = _PROMPT.format(emails_json=json.dumps(slim, indent=2))

            try:
                raw_response = await self._llm_classify(prompt)
                # Strip markdown fences if present
                text = raw_response.strip()
                if text.startswith("```"):
                    text = text.split("```")[1]
                    if text.startswith("json"):
                        text = text[4:]
                results = json.loads(text.strip())
            except Exception as exc:
                logger.warning("Email classification failed for batch: %s", exc)
                results = [{"id": e["id"], "classification": "fyi",
                            "classification_reason": "Classification unavailable"} for e in batch]

            # Build lookup map
            class_map = {r["id"]: r for r in results}

            for e in batch:
                c = class_map.get(e["id"], {})
                # Parse received_at from milliseconds timestamp
                try:
                    ts = int(e["received_at"]) / 1000
                    from datetime import datetime, timezone
                    received = datetime.fromtimestamp(ts, tz=timezone.utc)
                except Exception:
                    from datetime import datetime, timezone
                    received = datetime.now(timezone.utc)

                # Parse sender name and email
                raw_from = e["from"]
                if "<" in raw_from:
                    sender = raw_from.split("<")[0].strip().strip('"')
                    sender_email = raw_from.split("<")[1].rstrip(">").strip()
                else:
                    sender = raw_from
                    sender_email = raw_from

                classified.append(ClassifiedEmail(
                    id=e["id"],
                    subject=e["subject"],
                    sender=sender,
                    sender_email=sender_email,
                    snippet=e["snippet"],
                    received_at=received,
                    classification=c.get("classification", "fyi"),
                    classification_reason=c.get("classification_reason", ""),
                    thread_id=e["thread_id"],
                ))

        return classified
