"""
services/calendar_write_service.py — Writes events to Google Calendar via MCP.
"""

from __future__ import annotations

from schemas.calendar import CalendarProposal
from mcp.gcal_client import GCalMCPClient


class CalendarWriteService:
    """Handles creating Google Calendar events from confirmed proposals.

    This service is a thin coordinator that converts a CalendarProposal
    into an EventCreate payload and delegates the actual API call to the
    GCalMCPClient.
    """

    async def create_event(
        self,
        proposal: CalendarProposal,
        gcal_client: GCalMCPClient,
    ) -> str:
        """Create a Google Calendar event from a confirmed proposal.

        Args:
            proposal:    The CalendarProposal that the user confirmed.
            gcal_client: An authenticated GCalMCPClient instance for the
                         current user.

        Returns:
            The ID of the newly created Google Calendar event.

        Raises:
            NotImplementedError: Until the MCP client is implemented.
        """
        from schemas.calendar import EventCreate

        # TODO: build a richer description from proposal.rationale
        event_payload = EventCreate(
            title=proposal.task_title,
            start=proposal.proposed_start,
            end=proposal.proposed_end,
            description=f"Scheduled by DailyBrief.\n\nRationale: {proposal.rationale}",
        )

        # Delegate to MCP client
        event_id = await gcal_client.create_event(event_payload)
        return event_id
