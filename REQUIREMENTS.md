# DailyBrief — Requirements Document

**Version:** 2.0  
**Date:** June 21, 2026  
**Status:** Draft for Review

---

## 1. Product Overview

DailyBrief is a multi-agent AI system that aggregates data from Gmail, Google Calendar, and Notion each morning, analyzes and cross-references it, then presents a prioritized daily briefing in a two-panel web UI. The right panel hosts a conversational chat interface for follow-up questions and confirmed actions. Multi-user support with per-user credential isolation is included as the final build phase.

---

## 2. Functional Requirements

### 2.1 Authentication & User Management

| ID | Requirement |
|----|-------------|
| FR-AUTH-01 | Users MUST be able to sign up with email + password |
| FR-AUTH-02 | Passwords MUST be hashed with bcrypt before storage — plaintext passwords MUST never be persisted |
| FR-AUTH-03 | Users MUST be able to log in and receive a JWT access token |
| FR-AUTH-04 | Logged-in state MUST persist across page reloads (token stored in localStorage or httpOnly cookie) |
| FR-AUTH-05 | Logout MUST clear the session/token on both client and server |
| FR-AUTH-06 | All API endpoints (except `/auth/signup`, `/auth/login`) MUST require a valid JWT |
| FR-AUTH-07 | On first login, if a user has not connected one or more services (Gmail, Google Calendar, Notion), the UI MUST prompt them to complete those connections before generating a briefing |

### 2.2 Per-User OAuth & Credential Isolation

| ID | Requirement |
|----|-------------|
| FR-CRED-01 | Each user MUST complete their own OAuth 2.0 flow for Gmail and Google Calendar |
| FR-CRED-02 | Each user MUST provide their own Notion integration token |
| FR-CRED-03 | OAuth tokens and Notion tokens MUST be stored per-user in the database, encrypted at rest |
| FR-CRED-04 | Token refresh MUST be handled automatically per-user; expired tokens MUST be re-fetched without user intervention where possible |
| FR-CRED-05 | Credentials from one user MUST never be accessible to or used on behalf of another user |
| FR-CRED-06 | A user MUST be able to disconnect and re-connect any service from their settings page |

### 2.3 Data Gathering (Stage 1)

| ID | Requirement |
|----|-------------|
| FR-01 | The system MUST connect to Gmail via MCP and fetch unread/today-relevant emails for the authenticated user |
| FR-02 | The system MUST connect to Google Calendar via MCP (read + write) and fetch today's events for the authenticated user |
| FR-03 | The system MUST connect to Notion via MCP and fetch all pending tasks with their due dates for the authenticated user |
| FR-04 | All three data sources MUST be queried in parallel |
| FR-05 | If any single data source is unavailable, the pipeline MUST continue with a partial briefing and surface a clear degraded-mode warning in the UI |

### 2.4 Analysis (Stage 2)

| ID | Requirement |
|----|-------------|
| FR-06 | The Email Agent MUST classify each email as exactly one of: **Urgent**, **Can Wait**, **FYI** |
| FR-07 | The Calendar Agent MUST detect and flag: scheduling conflicts (overlapping events), back-to-back meetings (≤ 5 min gap), and free-time gaps ≥ 30 min |
| FR-08 | The Notes Agent MUST classify each task as **Overdue**, **Due today**, or **Due later** relative to the current date |
| FR-09 | Classification MUST be performed by the Gemini LLM (emails) or deterministic date logic (tasks); raw data MUST NOT be passed to the Coordinator |

### 2.5 Cross-Referencing (Stage 3)

| ID | Requirement |
|----|-------------|
| FR-10 | The Coordinator Agent MUST receive only structured/classified outputs from worker agents — never raw API payloads |
| FR-11 | The Coordinator MUST identify cross-source relationships (e.g., an email thread related to a calendar event) |
| FR-12 | Relationships MUST be surfaced as annotations on relevant briefing items |

### 2.6 Synthesis (Stage 4)

| ID | Requirement |
|----|-------------|
| FR-13 | The Coordinator MUST compile a prioritized briefing |
| FR-14 | The Coordinator MUST generate a short "focus suggestion" (1–3 sentences) based on urgent emails, calendar gaps, and overdue tasks |
| FR-15 | Summary stat cards MUST include: urgent email count, meeting count for today, pending/overdue task count |

### 2.7 Action Proposal & Confirmation (Stage 5)

| ID | Requirement |
|----|-------------|
| FR-16 | For each Overdue or Due-today task with no corresponding calendar block, the system MUST propose a time slot during an available free-time gap |
| FR-17 | The system MUST NEVER write to Google Calendar without explicit user confirmation via a UI confirm button or an explicit chat confirmation message |
| FR-18 | Draft email replies MUST be generated on demand only — via the "Draft reply" button per urgent email, or via a chat request |
| FR-19 | Generated drafts are editable inline; they MUST NOT be sent automatically under any circumstances |

### 2.8 Persistence (Stage 6)

| ID | Requirement |
|----|-------------|
| FR-20 | Each completed briefing run MUST be saved to SQLite with fields: `user_id`, `date`, `summary_text`, `urgent_email_count`, `calendar_conflict_flag`, `overdue_task_count` |
| FR-21 | All briefing history queries MUST filter by the logged-in `user_id` — users MUST NOT see each other's briefings |
| FR-22 | The UI MUST provide a "Briefing History" section showing the current user's past saved briefings |
| FR-23 | Clicking a past briefing MUST display its saved summary |

### 2.9 Chat Interface

| ID | Requirement |
|----|-------------|
| FR-24 | The chat panel MUST keep all Stage 1–3 structured outputs in memory for the current session |
| FR-25 | Chat MUST answer follow-up questions using in-memory session data (no re-running the pipeline) |
| FR-26 | Chat MUST support: "What is [meeting] about?", "Draft a reply to [sender]", "Schedule [task] for [time]" |
| FR-27 | When the user requests a calendar write via chat, the system MUST propose the action and require a confirmation reply before writing |

### 2.10 UI Layout

| ID | Requirement |
|----|-------------|
| FR-28 | Layout MUST be two-panel, side by side — left panel ~60% width, right panel ~40% width |
| FR-29 | Left panel MUST show: today's date, focus suggestion, stat cards, emails by classification, calendar events, tasks by classification |
| FR-30 | Each urgent email MUST display an inline "Draft reply" button |
| FR-31 | Calendar conflicts/back-to-back meetings MUST be visually flagged |
| FR-32 | Tasks MUST be visually distinguished: Overdue (red), Due today (amber), Due later (green/neutral) |
| FR-33 | A "View Briefing History" link MUST be present |
| FR-34 | Right panel MUST be a standard chat UI: scrollable message history, text input, send button |
| FR-35 | A settings/profile page MUST show connected service status and allow OAuth reconnection |

---

## 3. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Stage 1 parallel data gathering MUST complete within 15 seconds under normal network conditions |
| NFR-02 | The full pipeline (Stages 1–4) MUST complete within 30 seconds |
| NFR-03 | Chat responses MUST be returned within 5 seconds for in-memory queries |
| NFR-04 | Each agent MUST be independently testable with mocked data |
| NFR-05 | The system MUST handle Gemini API rate limits gracefully with exponential backoff |
| NFR-06 | All credentials (API keys, OAuth tokens) MUST be stored encrypted — never in plaintext in the database |
| NFR-07 | JWT secrets and encryption keys MUST be loaded from environment variables, never hardcoded |
| NFR-08 | The UI MUST be usable on screens ≥ 1280px wide |

---

## 4. Constraints & Assumptions

- LLM: Google Gemini API (all reasoning, classification, drafting, chat)
- MCP servers: official Gmail, Google Calendar, and Notion MCP integrations
- Backend: Python / FastAPI
- Frontend: React (Vite) + Tailwind CSS
- Database: SQLite via SQLAlchemy
- Auth: JWT (access token) stored client-side; refresh token stored in httpOnly cookie
- "Today" is determined by the server's local date at pipeline invocation time
- Multi-user is the final build phase — single-user pipeline is implemented and verified first

---

## 5. Out of Scope (v1)

- Sending emails (drafts only)
- Editing or deleting existing calendar events
- Notion write-back
- Mobile layout
- Push notifications or scheduled auto-runs
- Social / OAuth login (Google sign-in for app auth — separate from Google Calendar OAuth)
- Password reset / email verification flows
