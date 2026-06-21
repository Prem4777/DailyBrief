"""
agents/coordinator_agent.py — Cross-referencing, synthesis, and proposals.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta, timezone

from agents.base_agent import BaseAgent
from schemas.briefing import Briefing, CrossReference
from schemas.calendar import CalendarEvent, CalendarProposal, FreeSlot
from schemas.email import ClassifiedEmail
from schemas.tasks import ClassifiedTask
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class CoordinatorAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService) -> None:
        super().__init__(gemini_service)

    async def fetch(self, *args, **kwargs) -> list[dict]:  # type: ignore
        return []

    async def analyze(self, *args, **kwargs):  # type: ignore
        return None

    async def cross_reference(
        self,
        emails: list[ClassifiedEmail],
        events: list[CalendarEvent],
        tasks: list[ClassifiedTask],
    ) -> list[CrossReference]:
        if not (emails or events or tasks):
            return []

        prompt = f"""
You are analysing a user's morning briefing. Identify meaningful connections
between emails, calendar events, and tasks — e.g. an email about a meeting,
or a task mentioned in an email.

Return ONLY a valid JSON array (no markdown). Each element:
{{"email_id": "<id or null>", "event_id": "<id or null>", "task_id": "<id or null>", "relationship_description": "<one sentence>"}}

Return [] if no genuine connections exist.

Emails: {json.dumps([{"id": e.id, "subject": e.subject, "sender": e.sender} for e in emails[:10]])}
Events: {json.dumps([{"id": e.id, "title": e.title} for e in events[:10]])}
Tasks: {json.dumps([{"id": t.id, "title": t.title} for t in tasks[:10]])}
"""
        try:
            raw = await self._llm_classify(prompt)
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("```")[1]
                if text.startswith("json"):
                    text = text[4:]
            refs = json.loads(text.strip())
            return [CrossReference(**r) for r in refs if isinstance(r, dict)]
        except Exception as exc:
            logger.warning("cross_reference failed: %s", exc)
            return []

    async def synthesize(
        self,
        emails: list[ClassifiedEmail],
        events: list[CalendarEvent],
        tasks: list[ClassifiedTask],
        cross_refs: list[CrossReference],
        free_slots: list[FreeSlot],
        user_id: str,
        date: date,
    ) -> Briefing:
        urgent = [e for e in emails if e.classification == "urgent"]
        overdue = [t for t in tasks if t.classification == "overdue"]
        due_today = [t for t in tasks if t.classification == "due_today"]
        conflict_flag = any(e.conflict_flag for e in events)

        prompt = f"""
You are the DailyBrief AI assistant. Write a concise focus suggestion (2-4 sentences)
for the user's day on {date}. Be specific and actionable.

Data summary:
- Urgent emails: {len(urgent)} ({", ".join(e.subject[:40] for e in urgent[:3])})
- Meetings: {len(events)} ({", ".join(e.title[:30] for e in events[:3])})
- Overdue tasks: {len(overdue)} ({", ".join(t.title[:30] for t in overdue[:3])})
- Due today: {len(due_today)} ({", ".join(t.title[:30] for t in due_today[:3])})
- Calendar conflicts: {conflict_flag}
- Free slots: {len(free_slots)}

Write only the focus suggestion paragraph, no headers or lists.
"""
        try:
            focus = await self._llm_classify(prompt)
            focus = focus.strip()
        except Exception as exc:
            logger.warning("synthesize focus_suggestion failed: %s", exc)
            if urgent:
                focus = f"You have {len(urgent)} urgent email(s) requiring attention today."
            elif overdue:
                focus = f"You have {len(overdue)} overdue task(s) to address."
            elif events:
                focus = f"You have {len(events)} meeting(s) today."
            else:
                focus = "No urgent items today — a good day to tackle longer-term work."

        return Briefing(
            user_id=user_id,
            generated_at=datetime.now(timezone.utc),
            date=date,
            focus_suggestion=focus,
            urgent_email_count=len(urgent),
            meeting_count=len(events),
            overdue_task_count=len(overdue),
            calendar_conflict_flag=conflict_flag,
            emails=emails,
            events=events,
            free_slots=free_slots,
            tasks=tasks,
            cross_references=cross_refs,
        )

    def propose_actions(
        self,
        briefing: Briefing,
        free_slots: list[FreeSlot],
    ) -> list[CalendarProposal]:
        priority_tasks = [
            t for t in briefing.tasks
            if t.classification in ("overdue", "due_today")
        ]
        if not priority_tasks or not free_slots:
            return []

        proposals = []
        available = list(free_slots)  # copy to consume

        for task in priority_tasks:
            if not available:
                break
            slot = available[0]
            duration = timedelta(minutes=30)
            proposed_start = slot.start
            proposed_end = proposed_start + duration

            if proposed_end > slot.end:
                continue

            proposals.append(CalendarProposal(
                task_id=task.id,
                task_title=task.title,
                proposed_start=proposed_start,
                proposed_end=proposed_end,
                rationale=f"Scheduled during a free slot to address this "
                          f"{'overdue' if task.classification == 'overdue' else 'due-today'} task.",
            ))

            # Shrink the slot
            remaining_mins = int((slot.end - proposed_end).total_seconds() / 60)
            if remaining_mins >= 30:
                available[0] = FreeSlot(
                    start=proposed_end,
                    end=slot.end,
                    duration_minutes=remaining_mins,
                )
            else:
                available.pop(0)

        return proposals
