"""
mcp/gcal_client.py — Google Calendar client using the Calendar REST API directly.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timezone

import httpx

from config import settings
from schemas.calendar import EventCreate

logger = logging.getLogger(__name__)

_GCAL_BASE = "https://www.googleapis.com/calendar/v3"
_TOKEN_URL = "https://oauth2.googleapis.com/token"


class GCalMCPClient:
    def __init__(self, credentials: dict) -> None:
        self._creds = credentials

    async def _get_valid_token(self) -> str:
        access_token = self._creds.get("access_token", "")
        refresh_token = self._creds.get("refresh_token", "")
        if not refresh_token:
            return access_token
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(_TOKEN_URL, data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                })
            if resp.status_code == 200:
                access_token = resp.json().get("access_token", access_token)
                self._creds["access_token"] = access_token
        except Exception as exc:
            logger.warning("GCal token refresh failed: %s", exc)
        return access_token

    async def fetch_today_events(self, target_date: date) -> list[dict]:
        """Fetch all calendar events for target_date."""
        token = await self._get_valid_token()
        if not token:
            raise RuntimeError("No GCal access token available")

        # RFC3339 time range for the full day in UTC
        time_min = datetime(target_date.year, target_date.month, target_date.day,
                            0, 0, 0, tzinfo=timezone.utc).isoformat()
        time_max = datetime(target_date.year, target_date.month, target_date.day,
                            23, 59, 59, tzinfo=timezone.utc).isoformat()

        calendar_id = settings.google_calendar_id

        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{_GCAL_BASE}/calendars/{calendar_id}/events",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "timeMin": time_min,
                    "timeMax": time_max,
                    "singleEvents": "true",
                    "orderBy": "startTime",
                    "maxResults": 50,
                },
            )

        if resp.status_code != 200:
            logger.warning("GCal list failed: %s %s", resp.status_code, resp.text)
            return []

        return resp.json().get("items", [])

    async def create_event(self, event: EventCreate) -> str:
        """Create a new calendar event. Returns the created event ID."""
        token = await self._get_valid_token()
        if not token:
            raise RuntimeError("No GCal access token available")

        calendar_id = settings.google_calendar_id
        body = {
            "summary": event.title,
            "description": event.description or "",
            "start": {"dateTime": event.start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event.end.isoformat(), "timeZone": "UTC"},
        }

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{_GCAL_BASE}/calendars/{calendar_id}/events",
                headers={"Authorization": f"Bearer {token}",
                         "Content-Type": "application/json"},
                json=body,
            )

        if resp.status_code not in (200, 201):
            raise RuntimeError(f"GCal create event failed: {resp.status_code} {resp.text}")

        return resp.json().get("id", "")
