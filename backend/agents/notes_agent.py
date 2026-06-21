"""
agents/notes_agent.py — Fetches Notion tasks and classifies them by due date.
Fully deterministic — no LLM.
"""

from __future__ import annotations

import logging
from datetime import date

from agents.base_agent import BaseAgent
from mcp.notion_client import NotionMCPClient
from schemas.tasks import ClassifiedTask
from services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


def _get_plain_text(rich_text_list: list) -> str:
    return "".join(t.get("plain_text", "") for t in rich_text_list)


class NotesAgent(BaseAgent):
    def __init__(self, gemini_service: GeminiService) -> None:
        super().__init__(gemini_service)

    async def fetch(self, notion_client: NotionMCPClient, database_id: str) -> list[dict]:
        return await notion_client.fetch_pending_tasks(database_id)

    async def analyze(self, raw_tasks: list[dict], today: date) -> list[ClassifiedTask]:
        if not raw_tasks:
            return []

        tasks: list[ClassifiedTask] = []
        for raw in raw_tasks:
            try:
                task = self._parse_task(raw, today)
                if task:
                    tasks.append(task)
            except Exception as exc:
                logger.warning("Failed to parse Notion task: %s", exc)

        # Sort: overdue first, then due_today, then due_later
        order = {"overdue": 0, "due_today": 1, "due_later": 2}
        tasks.sort(key=lambda t: order.get(t.classification, 2))
        return tasks

    def _parse_task(self, raw: dict, today: date) -> ClassifiedTask | None:
        props = raw.get("properties", {})

        # Title — try common property names
        title = ""
        for key in ("Name", "Title", "Task", "title", "name"):
            val = props.get(key, {})
            if val.get("type") == "title":
                title = _get_plain_text(val.get("title", []))
                break
        if not title:
            # Fallback: find any title-type property
            for val in props.values():
                if val.get("type") == "title":
                    title = _get_plain_text(val.get("title", []))
                    break

        if not title:
            return None

        # Due date — try common property names
        due_date: date | None = None
        for key in ("Due Date", "Due", "Date", "Deadline", "due_date", "due"):
            val = props.get(key, {})
            if val.get("type") == "date" and val.get("date"):
                start = val["date"].get("start")
                if start:
                    try:
                        due_date = date.fromisoformat(start[:10])
                    except Exception:
                        pass
                    break

        # Classification
        if due_date is None:
            classification = "due_later"
        elif due_date < today:
            classification = "overdue"
        elif due_date == today:
            classification = "due_today"
        else:
            classification = "due_later"

        # Project — try common property names
        project: str | None = None
        for key in ("Project", "Category", "Area", "project"):
            val = props.get(key, {})
            t = val.get("type")
            if t == "select" and val.get("select"):
                project = val["select"].get("name")
                break
            elif t == "multi_select" and val.get("multi_select"):
                project = val["multi_select"][0].get("name")
                break

        return ClassifiedTask(
            id=raw.get("id", ""),
            title=title,
            due_date=due_date.isoformat() if due_date else None,
            classification=classification,
            project=project,
            url=raw.get("url", ""),
        )
