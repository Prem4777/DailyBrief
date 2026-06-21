"""
mcp/gmail_client.py — Gmail client using the Google Gmail REST API directly.
Uses the stored OAuth access_token; refreshes automatically if expired.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

import httpx

from config import settings

logger = logging.getLogger(__name__)

_GMAIL_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GmailMCPClient:
    def __init__(self, credentials: dict) -> None:
        self._creds = credentials

    async def _get_valid_token(self) -> str:
        """Return a valid access token, refreshing if necessary."""
        access_token = self._creds.get("access_token", "")
        refresh_token = self._creds.get("refresh_token", "")

        if not refresh_token:
            return access_token

        # Try refreshing proactively (token may be expired)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(_TOKEN_URL, data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                })
            if resp.status_code == 200:
                new_tokens = resp.json()
                access_token = new_tokens.get("access_token", access_token)
                self._creds["access_token"] = access_token
        except Exception as exc:
            logger.warning("Token refresh failed: %s", exc)

        return access_token

    async def fetch_today_emails(self, target_date: date) -> list[dict]:
        """Fetch unread emails received on target_date."""
        token = await self._get_valid_token()
        if not token:
            raise RuntimeError("No Gmail access token available")

        # Build date range query — after:YYYY/MM/DD before:YYYY/MM/DD
        from datetime import timedelta
        next_day = target_date + timedelta(days=1)
        date_str = target_date.strftime("%Y/%m/%d")
        next_date_str = next_day.strftime("%Y/%m/%d")
        query = f"after:{date_str} before:{next_date_str}"

        headers = {"Authorization": f"Bearer {token}"}
        emails = []

        async with httpx.AsyncClient() as client:
            # List message IDs
            list_resp = await client.get(
                f"{_GMAIL_BASE}/messages",
                headers=headers,
                params={"q": query, "maxResults": 50},
            )

            if list_resp.status_code != 200:
                logger.warning("Gmail list failed: %s %s", list_resp.status_code, list_resp.text)
                return []

            message_ids = [m["id"] for m in list_resp.json().get("messages", [])]

            # Fetch each message
            for msg_id in message_ids[:30]:  # cap at 30
                msg_resp = await client.get(
                    f"{_GMAIL_BASE}/messages/{msg_id}",
                    headers=headers,
                    params={"format": "metadata", "metadataHeaders": ["Subject", "From", "Date"]},
                )
                if msg_resp.status_code == 200:
                    emails.append(msg_resp.json())

        return emails
