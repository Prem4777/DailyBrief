"""
routers/chat.py — Conversational chat endpoint powered by Gemini.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from dependencies import get_current_user
from models.user import User
from pipeline.session_store import session_store
from schemas.calendar import CalendarProposal
from schemas.chat import ChatMessage, ChatRequest, ChatResponse
from services.gemini_service import GeminiService

router = APIRouter()
logger = logging.getLogger(__name__)

_gemini: GeminiService | None = None


def _get_gemini() -> GeminiService:
    global _gemini
    if _gemini is None:
        _gemini = GeminiService()
    return _gemini


def _build_context(session) -> str:
    """Build a compact briefing context string for the LLM."""
    if not session or not session.briefing:
        return "No briefing has been generated yet for today."

    b = session.briefing
    lines = [
        f"Date: {b.date}",
        f"Urgent emails ({b.urgent_email_count}):",
    ]
    for e in b.emails:
        if e.classification == "urgent":
            lines.append(f"  - [{e.id}] From: {e.sender} | Subject: {e.subject}")

    lines.append(f"\nAll emails ({len(b.emails)}):")
    for e in b.emails:
        lines.append(f"  - [{e.id}] {e.classification.upper()} | {e.sender}: {e.subject}")

    lines.append(f"\nCalendar events ({b.meeting_count}):")
    for ev in b.events:
        flag = " ⚠️ CONFLICT" if ev.conflict_flag else ""
        lines.append(f"  - [{ev.id}] {ev.start.strftime('%H:%M')}-{ev.end.strftime('%H:%M')} {ev.title}{flag}")

    lines.append(f"\nTasks ({len(b.tasks)}):")
    for t in b.tasks:
        lines.append(f"  - [{t.id}] {t.classification.upper()} | {t.title} (due: {t.due_date or 'no date'})")

    if b.free_slots:
        lines.append(f"\nFree slots:")
        for s in b.free_slots:
            lines.append(f"  - {s.start.strftime('%H:%M')}-{s.end.strftime('%H:%M')} ({s.duration_minutes}min)")

    return "\n".join(lines)


_INTENT_PROMPT = """
Classify this user message into exactly one intent:
- question: asking about their emails, events, tasks, or day
- draft_reply: asking to draft/write a reply to an email
- schedule_task: asking to schedule or add a task to calendar
- confirm: confirming a pending action (yes, confirm, do it, ok)
- reject: rejecting a pending action (no, cancel, don't, skip)
- general: anything else

User message: "{message}"

Return ONLY the intent word, nothing else.
"""

_CHAT_PROMPT = """
You are DailyBrief, an AI assistant helping the user understand and act on their morning briefing.
Answer based ONLY on the briefing data below. Be concise and helpful.

BRIEFING DATA:
{context}

CONVERSATION HISTORY:
{history}

USER: {message}

ASSISTANT:"""


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    now = datetime.now(timezone.utc)
    user_msg = ChatMessage(role="user", content=body.message, created_at=now)
    session_store.append_message(current_user.id, user_msg)

    session = session_store.get(current_user.id)
    context = _build_context(session)
    history = session_store.get_chat_history(current_user.id)

    # Format history (last 6 messages for context window)
    history_text = "\n".join(
        f"{'USER' if m.role == 'user' else 'ASSISTANT'}: {m.content}"
        for m in history[-6:]
    )

    try:
        gemini = _get_gemini()

        # Classify intent
        intent_raw = await gemini.generate(
            _INTENT_PROMPT.format(message=body.message)
        )
        intent = intent_raw.strip().lower().split()[0] if intent_raw.strip() else "general"

        # Handle confirm/reject
        if intent == "confirm" and session and session.pending_action:
            action = session.pending_action
            reply = (
                f"Got it! I'll schedule **{action.task_title}** from "
                f"{action.proposed_start.strftime('%H:%M')} to "
                f"{action.proposed_end.strftime('%H:%M')}. "
                f"Click Confirm in the banner above to finalize."
            )
            assistant_msg = ChatMessage(role="assistant", content=reply, created_at=now)
            session_store.append_message(current_user.id, assistant_msg)
            return ChatResponse(message=assistant_msg, pending_action=session.pending_action)

        if intent == "reject":
            session_store.clear_pending_action(current_user.id)
            reply = "No problem, I've cancelled that suggestion."
            assistant_msg = ChatMessage(role="assistant", content=reply, created_at=now)
            session_store.append_message(current_user.id, assistant_msg)
            return ChatResponse(message=assistant_msg, pending_action=None)

        # draft_reply: point the user to the draft button, or offer help
        if intent == "draft_reply":
            # Try to surface the most relevant urgent email for context
            urgent_emails = [e for e in (session.briefing.emails if session and session.briefing else []) if e.classification == "urgent"]
            if urgent_emails:
                email = urgent_emails[0]
                hint = (
                    f"I can draft a reply to **{email.sender}** regarding \"{email.subject}\". "
                    f"Click the Draft button next to that email in the briefing panel, or tell me "
                    f"which email you'd like to reply to by mentioning the sender's name."
                )
            else:
                hint = "I don't see any urgent emails right now. Let me know which email you'd like to reply to by mentioning the sender's name."
            assistant_msg = ChatMessage(role="assistant", content=hint, created_at=now)
            session_store.append_message(current_user.id, assistant_msg)
            return ChatResponse(message=assistant_msg, pending_action=None)

        # schedule_task: surface the first overdue/due-today task with a proposal
        if intent == "schedule_task" and session and session.briefing:
            priority_tasks = [t for t in session.briefing.tasks if t.classification in ("overdue", "due_today")]
            proposal = next(
                (p for t in priority_tasks for p in session.briefing.proposals if p.task_id == t.id),
                None,
            )
            if proposal:
                session_store.set_pending_action(current_user.id, proposal)
                reply = (
                    f"I can schedule **{proposal.task_title}** from "
                    f"{proposal.proposed_start.strftime('%H:%M')} to "
                    f"{proposal.proposed_end.strftime('%H:%M')}. "
                    f"Say \"confirm\" to add it to your calendar, or \"no\" to skip."
                )
                assistant_msg = ChatMessage(role="assistant", content=reply, created_at=now)
                session_store.append_message(current_user.id, assistant_msg)
                return ChatResponse(message=assistant_msg, pending_action=proposal)

        # Generate response
        full_prompt = _CHAT_PROMPT.format(
            context=context,
            history=history_text,
            message=body.message,
        )
        reply = await gemini.generate(full_prompt)
        reply = reply.strip()

    except Exception as exc:
        logger.warning("Chat generation failed: %s", exc)
        reply = "Sorry, I couldn't process that right now. Please try again."

    assistant_msg = ChatMessage(role="assistant", content=reply, created_at=now)
    session_store.append_message(current_user.id, assistant_msg)
    pending = session_store.get_pending_action(current_user.id)

    return ChatResponse(message=assistant_msg, pending_action=pending)
