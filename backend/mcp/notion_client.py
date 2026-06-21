"""
mcp/notion_client.py — Notion client using the Notion REST API directly.
"""

from __future__ import annotations

import logging
import re

import httpx

logger = logging.getLogger(__name__)

_NOTION_BASE = "https://api.notion.com/v1"
_NOTION_VERSION = "2022-06-28"


class NotionMCPClient:
    def __init__(self, credentials: dict) -> None:
        self._token = credentials.get("access_token", "")
        self._database_id = credentials.get("database_id", "")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._token}",
            "Notion-Version": _NOTION_VERSION,
            "Content-Type": "application/json",
        }

    async def fetch_pending_tasks(self, database_id: str) -> list[dict]:
        """Fetch all pending tasks from a Notion database."""
        raw_id = (database_id or self._database_id).strip()

        # Accept full Notion page URLs — extract the 32-hex-char ID from the end.
        # e.g. https://www.notion.so/My-Page-abc123def456...?v=... → abc123def456...
        url_match = re.search(r"([0-9a-f]{32})", raw_id.replace("-", ""))
        if url_match:
            # Re-format as standard UUID: 8-4-4-4-12
            flat = url_match.group(1)
            db_id = f"{flat[:8]}-{flat[8:12]}-{flat[12:16]}-{flat[16:20]}-{flat[20:]}"
        else:
            db_id = raw_id
        if not db_id:
            raise RuntimeError("No Notion database ID configured")
        if not self._token:
            raise RuntimeError("No Notion access token available")

        pages = []
        cursor = None

        async with httpx.AsyncClient() as client:
            while True:
                body: dict = {"page_size": 100}
                if cursor:
                    body["start_cursor"] = cursor

                resp = await client.post(
                    f"{_NOTION_BASE}/databases/{db_id}/query",
                    headers=self._headers(),
                    json=body,
                )

                if resp.status_code != 200:
                    logger.warning("Notion query failed: %s %s", resp.status_code, resp.text)
                    break

                data = resp.json()
                pages.extend(data.get("results", []))

                if not data.get("has_more"):
                    break
                cursor = data.get("next_cursor")

        return pages
