# DailyBrief — Architecture & Design Document

**Version:** 2.0  
**Date:** June 21, 2026  
**Status:** Draft for Review

---

## 1. System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (React)                           │
│  ┌──────────────────────────────┐  ┌───────────────────────────┐ │
│  │   Left Panel (Briefing)      │  │  Right Panel (Chat)       │ │
│  │  - Date + Focus Suggestion   │  │  - Message bubbles        │ │
│  │  - Stat Cards                │  │  - Scrollable history     │ │
│  │  - Emails (classified)       │  │  - Text input + Send      │ │
│  │  - Calendar events           │  │  - Confirm/Cancel actions │ │
│  │  - Tasks (classified)        │  │                           │ │
│  │  - History link              │  │                           │ │
│  └──────────────┬───────────────┘  └────────────┬──────────────┘ │
└─────────────────┼────────────────────────────────┼───────────────┘
                  │  REST / SSE                     │ REST
                  ▼                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                             │
│                                                                  │
│  /auth/*          — signup, login, logout, OAuth flows           │
│  /api/briefing/*  — run, current, history                        │
│  /api/chat        — conversational layer                         │
│  /api/actions/*   — email draft, calendar propose/confirm        │
│  /api/settings/*  — connected services, disconnect               │
└──────────────────────┬───────────────────────────────────────────┘
                       │  (per-user credentials injected)
         ┌─────────────┼─────────────┐
         ▼             ▼             ▼
  ┌────────────┐ ┌────────────┐ ┌────────────┐
  │Email Agent │ │ Cal. Agent │ │Notes Agent │
  └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
        │              │               │
        ▼              ▼               ▼
  ┌──────────┐  ┌──────────┐   ┌──────────┐
  │Gmail MCP │  │ GCal MCP │   │Notion MCP│
  └──────────┘  └──────────┘   └──────────┘
        │              │               │
        └──────────────┼───────────────┘
                       ▼
            ┌─────────────────────┐
            │  Coordinator Agent  │
            │  (cross-ref +       │
            │   synthesis +       │
            │   action proposals) │
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   SQLite Database   │
            │  users, credentials │
            │  briefings (w/ uid) │
            └─────────────────────┘
```

---

## 2. Folder Structure

```
dailybrief/
├── REQUIREMENTS.md
├── DESIGN.md
├── backend/
│   ├── main.py                      # FastAPI app, router registration, CORS
│   ├── config.py                    # Settings from env vars (pydantic-settings)
│   ├── database.py                  # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # User table
│   │   ├── credential.py            # Per-user encrypted OAuth/API tokens
│   │   └── briefing.py              # Briefing history table
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                  # SignupRequest, LoginRequest, TokenResponse
│   │   ├── email.py                 # ClassifiedEmail
│   │   ├── calendar.py              # CalendarEvent, FreeSlot, CalendarProposal
│   │   ├── tasks.py                 # ClassifiedTask
│   │   ├── briefing.py              # Briefing, BriefingHistoryItem
│   │   └── chat.py                  # ChatRequest, ChatResponse, ChatMessage
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py                  # /auth/signup, /auth/login, /auth/logout
│   │   ├── oauth.py                 # /auth/google/start, /auth/google/callback
│   │   ├── briefing.py              # /api/briefing/*
│   │   ├── chat.py                  # /api/chat
│   │   ├── actions.py               # /api/actions/draft, propose, confirm
│   │   └── settings.py              # /api/settings/services
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # JWT creation/validation, bcrypt
│   │   ├── credential_service.py    # Encrypt/decrypt per-user tokens
│   │   ├── gemini_service.py        # Gemini API client + retry/backoff
│   │   ├── draft_service.py         # Email draft generation
│   │   └── calendar_write_service.py# Confirmed calendar event creation
│   ├── pipeline/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Runs all 6 stages in order
│   │   ├── session_store.py         # In-memory per-user session cache
│   │   └── stages/
│   │       ├── stage1_gather.py
│   │       ├── stage2_analyze.py
│   │       ├── stage3_crossref.py
│   │       ├── stage4_synthesize.py
│   │       ├── stage5_propose.py
│   │       └── stage6_persist.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base_agent.py            # Abstract base; holds GeminiService ref
│   │   ├── email_agent.py           # Gmail fetch + LLM classification
│   │   ├── calendar_agent.py        # GCal fetch + deterministic conflict detection
│   │   ├── notes_agent.py           # Notion fetch + deterministic date classification
│   │   └── coordinator_agent.py     # Cross-ref, synthesis, proposals
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── gmail_client.py          # Gmail MCP subprocess wrapper
│   │   ├── gcal_client.py           # Google Calendar MCP wrapper (r+w)
│   │   └── notion_client.py         # Notion MCP wrapper
│   ├── dependencies.py              # FastAPI Depends: get_current_user, get_db
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── tsconfig.json
    └── src/
        ├── main.tsx
        ├── App.tsx                  # Route definitions
        ├── api/
        │   ├── client.ts            # Axios instance with JWT interceptor
        │   ├── authApi.ts
        │   ├── briefingApi.ts
        │   ├── chatApi.ts
        │   └── actionsApi.ts
        ├── store/
        │   ├── authStore.ts         # Zustand: user, token, login/logout
        │   └── briefingStore.ts     # Zustand: briefing, loading, error
        ├── components/
        │   ├── layout/
        │   │   ├── TwoColumnLayout.tsx
        │   │   ├── BriefingPanel.tsx
        │   │   └── ChatPanel.tsx
        │   ├── briefing/
        │   │   ├── DateHeader.tsx
        │   │   ├── FocusSuggestion.tsx
        │   │   ├── StatCards.tsx
        │   │   ├── EmailSection.tsx
        │   │   ├── EmailCard.tsx
        │   │   ├── DraftReplyDrawer.tsx
        │   │   ├── CalendarSection.tsx
        │   │   ├── EventCard.tsx
        │   │   ├── TaskSection.tsx
        │   │   ├── TaskCard.tsx
        │   │   └── BriefingHistory.tsx
        │   ├── chat/
        │   │   ├── MessageBubble.tsx
        │   │   ├── MessageList.tsx
        │   │   ├── ChatInput.tsx
        │   │   └── ConfirmActionBanner.tsx
        │   └── auth/
        │       ├── LoginForm.tsx
        │       ├── SignupForm.tsx
        │       └── ServiceConnectionPrompt.tsx
        ├── hooks/
        │   ├── useBriefing.ts
        │   └── useChat.ts
        ├── pages/
        │   ├── LoginPage.tsx
        │   ├── SignupPage.tsx
        │   ├── DashboardPage.tsx    # Main two-panel view
        │   ├── HistoryPage.tsx
        │   └── SettingsPage.tsx
        └── types/
            ├── briefing.ts
            ├── chat.ts
            └── auth.ts
```

---

## 3. Database Schema

```sql
-- Users
CREATE TABLE users (
    id            TEXT PRIMARY KEY,          -- UUID
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,             -- bcrypt
    created_at    TEXT NOT NULL
);

-- Per-user encrypted credentials
CREATE TABLE user_credentials (
    id            TEXT PRIMARY KEY,          -- UUID
    user_id       TEXT NOT NULL REFERENCES users(id),
    service       TEXT NOT NULL,             -- 'gmail', 'gcal', 'notion'
    token_data    TEXT NOT NULL,             -- AES-encrypted JSON blob
    connected_at  TEXT NOT NULL,
    UNIQUE(user_id, service)
);

-- Briefing history (one row per run)
CREATE TABLE briefings (
    id                     TEXT PRIMARY KEY,
    user_id                TEXT NOT NULL REFERENCES users(id),
    date                   TEXT NOT NULL,    -- YYYY-MM-DD
    generated_at           TEXT NOT NULL,    -- ISO datetime
    summary_text           TEXT NOT NULL,
    focus_suggestion       TEXT NOT NULL,
    urgent_email_count     INTEGER NOT NULL,
    meeting_count          INTEGER NOT NULL,
    overdue_task_count     INTEGER NOT NULL,
    calendar_conflict_flag INTEGER NOT NULL, -- 0 or 1
    partial                INTEGER NOT NULL, -- 0 or 1 (degraded mode)
    unavailable_sources    TEXT,             -- JSON array e.g. ["gmail"]
    full_briefing_json     TEXT NOT NULL     -- serialized Briefing object
);
```

**Credential encryption:** `token_data` is encrypted with `cryptography.fernet` using a key derived from `CREDENTIAL_ENCRYPTION_KEY` in `.env`. The decrypted blob is a JSON object containing the OAuth `access_token`, `refresh_token`, `expiry`, and any service-specific config (e.g., Notion `database_id`).

---

## 4. Pydantic Data Models

### Agent Structured Outputs (what Coordinator receives)

```python
class ClassifiedEmail(BaseModel):
    id: str
    subject: str
    sender: str
    sender_email: str
    snippet: str                              # first ~200 chars
    received_at: datetime
    classification: Literal["urgent", "can_wait", "fyi"]
    classification_reason: str
    thread_id: str

class CalendarEvent(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    attendees: list[str]
    description: str
    location: str | None
    conflict_flag: bool
    back_to_back_flag: bool
    conflict_with_id: str | None

class FreeSlot(BaseModel):
    start: datetime
    end: datetime
    duration_minutes: int

class ClassifiedTask(BaseModel):
    id: str
    title: str
    due_date: date | None
    classification: Literal["overdue", "due_today", "due_later"]
    project: str | None
    url: str

class CrossReference(BaseModel):
    email_id: str | None
    event_id: str | None
    task_id: str | None
    relationship_description: str

class CalendarProposal(BaseModel):
    task_id: str
    task_title: str
    proposed_start: datetime
    proposed_end: datetime
    rationale: str

class Briefing(BaseModel):
    id: str
    user_id: str
    generated_at: datetime
    date: date
    focus_suggestion: str
    urgent_email_count: int
    meeting_count: int
    overdue_task_count: int
    calendar_conflict_flag: bool
    emails: list[ClassifiedEmail]
    events: list[CalendarEvent]
    free_slots: list[FreeSlot]
    tasks: list[ClassifiedTask]
    cross_references: list[CrossReference]
    proposals: list[CalendarProposal]
    partial: bool
    unavailable_sources: list[str]
```

---

## 5. API Endpoints

### Auth

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/auth/signup` | Public | Create account (email + password) |
| `POST` | `/auth/login` | Public | Returns JWT access token |
| `POST` | `/auth/logout` | JWT | Invalidates refresh token |
| `GET`  | `/auth/google/start` | JWT | Initiates Google OAuth flow |
| `GET`  | `/auth/google/callback` | Public | OAuth redirect, saves tokens per user |

### Settings

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET`  | `/api/settings/services` | JWT | Returns connected service status per user |
| `POST` | `/api/settings/notion-token` | JWT | Save Notion integration token for user |
| `DELETE` | `/api/settings/services/{service}` | JWT | Disconnect a service |

### Briefing

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/briefing/run` | JWT | Trigger full pipeline for the current user |
| `GET`  | `/api/briefing/current` | JWT | Return in-memory briefing for current session |
| `GET`  | `/api/briefing/history` | JWT | List user's saved briefings (summary only) |
| `GET`  | `/api/briefing/history/{id}` | JWT | Get full saved briefing (user-scoped) |

### Chat

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/chat` | JWT | Send message, get response from in-memory session |

### Actions

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `POST` | `/api/actions/draft` | JWT | Generate email draft for given email ID |
| `POST` | `/api/actions/calendar/propose` | JWT | Propose time slot for task (no write) |
| `POST` | `/api/actions/calendar/confirm` | JWT | Confirm pending proposal → write to GCal |

---

## 6. Agent Design

### 6.1 Base Agent

```python
class BaseAgent(ABC):
    def __init__(self, gemini_service: GeminiService): ...

    @abstractmethod
    async def fetch(self, mcp_client, user_credentials: dict) -> RawData: ...

    @abstractmethod
    async def analyze(self, raw_data: RawData) -> StructuredOutput: ...

    async def _llm_classify(self, prompt: str, schema: type[T]) -> T:
        # Calls GeminiService with JSON mode + schema enforcement
        # Includes exponential backoff on rate limit errors
        ...
```

Each agent is independently testable: `fetch()` accepts a mock MCP client, `analyze()` accepts pre-loaded raw data.

### 6.2 Email Agent

1. `fetch()` → calls `GmailMCPClient.list_messages(today)` then `get_message(id)` for each
2. `analyze()` → single batched Gemini call with all emails as JSON array
3. Prompt instructs classification as: **Urgent** (action required today, deadline present, high-priority sender), **Can Wait** (response needed but not urgent), **FYI** (newsletters, notifications, CC)
4. Returns `list[ClassifiedEmail]`

### 6.3 Calendar Agent

1. `fetch()` → calls `GCalMCPClient.list_events(today)`
2. `analyze()` → pure Python:
   - Sort events by start time
   - Detect conflicts: two events with overlapping time ranges
   - Detect back-to-back: gap between consecutive events ≤ 5 min
   - Compute free slots: gaps ≥ 30 min between events (and before first / after last within 8am–7pm window)
3. Returns `list[CalendarEvent]` + `list[FreeSlot]`
4. **No LLM needed** for conflict detection — deterministic logic only

### 6.4 Notes Agent

1. `fetch()` → calls `NotionMCPClient.query_database(pending_filter)`
2. `analyze()` → pure Python date comparison:
   - `due_date < today` → `overdue`
   - `due_date == today` → `due_today`
   - `due_date > today` or `None` → `due_later`
3. Returns `list[ClassifiedTask]`
4. **No LLM needed** at this stage — classification is deterministic

### 6.5 Coordinator Agent

Receives only structured outputs — zero raw API data.

**Stage 3 — Cross-referencing:**
- Input: list of email subjects/senders, event titles/times, task titles
- Single Gemini call: "Identify any relationships between these items"
- Output: `list[CrossReference]`

**Stage 4 — Synthesis:**
- Input: all classified outputs + cross-references
- Generates `focus_suggestion` paragraph
- Assembles complete `Briefing` object

**Stage 5 — Proposals:**
- For each `overdue`/`due_today` task: check if any event title matches task title (already scheduled)
- If not scheduled: pick the earliest `FreeSlot` that fits a 30-min block
- Build `CalendarProposal` objects — stored in session, not written

---

## 7. Pipeline Orchestrator

```
orchestrator.run(user_id, date)
  │
  ├─ Load per-user credentials from DB (decrypt)
  │
  ├─ STAGE 1 — asyncio.gather() with individual try/except per source:
  │     email_agent.fetch(gmail_client, creds)
  │     calendar_agent.fetch(gcal_client, creds)
  │     notes_agent.fetch(notion_client, creds)
  │     → sets partial=True + unavailable_sources if any fail
  │
  ├─ STAGE 2 — asyncio.gather():
  │     email_agent.analyze(raw_emails)
  │     calendar_agent.analyze(raw_events)
  │     notes_agent.analyze(raw_tasks)
  │
  ├─ STAGE 3: coordinator.cross_reference(emails, events, tasks)
  │
  ├─ STAGE 4: coordinator.synthesize(all_classified, cross_refs)
  │     → Briefing object (proposals=[])
  │
  ├─ STAGE 5: coordinator.propose_actions(briefing, free_slots)
  │     → list[CalendarProposal] attached to Briefing
  │
  └─ STAGE 6:
        db.save_briefing(briefing)
        session_store.set(user_id, briefing)
        return briefing
```

**Error handling per source:** Each Stage 1 gather task is wrapped in `asyncio.shield` + `try/except`. Failure produces an empty result for that source and appends the source name to `unavailable_sources`. The pipeline continues with remaining data.

---

## 8. Chat Architecture

```
POST /api/chat  {session_id, message}
  │
  ├─ Load ChatSession from session_store (in-memory, user-scoped)
  │   Contains: full Briefing, message history, pending_calendar_action
  │
  ├─ Intent Classification (Gemini):
  │   One of: question_email | question_event | question_task |
  │            request_draft | request_schedule | confirm | reject | general
  │
  ├─ Route by intent:
  │   question_*       → answer from Briefing data (no API calls)
  │   request_draft    → DraftService.generate(email_id, briefing)
  │   request_schedule → CalendarService.propose(task, free_slots)
  │                      store pending_action in session
  │                      return proposal + "Reply 'confirm' to schedule"
  │   confirm          → if pending_action exists:
  │                        CalendarWriteService.create_event(action, user_creds)
  │                        clear pending_action
  │   reject           → clear pending_action
  │   general          → Gemini QA with briefing context summary as system prompt
  │
  └─ Append to message history, return ChatResponse
```

**Session isolation:** `session_store` is a dict keyed by `user_id`. Each user's session holds their own `Briefing` and message history. Sessions are evicted after 24 hours of inactivity.

**Context passed to LLM:** A condensed briefing summary (not raw API data) is injected as the system prompt for chat. This keeps token usage low while preserving enough context for Q&A.

---

## 9. Authentication Flow

```
Signup:
  POST /auth/signup {email, password}
  → hash password (bcrypt, cost=12)
  → insert user row
  → return JWT access token

Login:
  POST /auth/login {email, password}
  → bcrypt.verify(password, stored_hash)
  → return JWT {sub: user_id, exp: +1h}
  → set httpOnly cookie with refresh token (exp: +7d)

Protected request:
  Authorization: Bearer <access_token>
  → FastAPI Depends(get_current_user) decodes JWT
  → Injects user object into route handler

Google OAuth (per-user, for Gmail + GCal):
  GET /auth/google/start
  → redirect to Google consent screen with user_id in state param
  GET /auth/google/callback?code=...&state=user_id
  → exchange code for tokens
  → encrypt tokens
  → upsert into user_credentials (service='gcal')
  → redirect to /settings

Notion (per-user):
  POST /api/settings/notion-token {token, database_id}
  → validate token against Notion API
  → encrypt + store in user_credentials (service='notion')
```

---

## 10. MCP Integration

Each MCP client is a thin async wrapper. MCP servers run as subprocesses via the `mcp` Python SDK, initialized with per-user credentials:

```python
class GmailMCPClient:
    async def list_messages(self, date: date) -> list[dict]: ...
    async def get_message(self, msg_id: str) -> dict: ...

class GCalMCPClient:
    async def list_events(self, date: date) -> list[dict]: ...
    async def create_event(self, event: EventCreate) -> str: ...

class NotionMCPClient:
    async def query_database(self, database_id: str, filter: dict) -> list[dict]: ...
```

**Per-user instantiation:** Each pipeline run creates fresh MCP client instances initialized with the calling user's decrypted tokens. Clients are not shared across users or requests.

---

## 11. Frontend Architecture

### Route Map

| Path | Component | Auth Required |
|------|-----------|---------------|
| `/login` | LoginPage | No |
| `/signup` | SignupPage | No |
| `/` | DashboardPage | Yes |
| `/history` | HistoryPage | Yes |
| `/settings` | SettingsPage | Yes |

### State Management (Zustand)

```typescript
// authStore.ts
interface AuthStore {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

// briefingStore.ts
interface BriefingStore {
  briefing: Briefing | null;
  isLoading: boolean;
  error: string | null;
  draftsByEmailId: Record<string, string>;
  runBriefing: () => Promise<void>;
  setDraft: (emailId: string, draft: string) => void;
}
```

### Axios Interceptor

All API requests go through a shared Axios instance that:
1. Injects `Authorization: Bearer <token>` header from authStore
2. On 401 response: attempts token refresh, then redirects to `/login` if refresh fails

### Key UI Components

| Component | Responsibility |
|-----------|---------------|
| `TwoColumnLayout` | CSS Grid 60/40 split |
| `StatCards` | Three metric cards at top of briefing panel |
| `EmailSection` | Emails grouped by Urgent / Can Wait / FYI |
| `EmailCard` | Subject, sender, snippet, "Draft Reply" button |
| `DraftReplyDrawer` | Expandable inline editable draft |
| `CalendarSection` | Timeline view; red badge on conflicts |
| `EventCard` | Title, time, attendees; conflict/back-to-back badge |
| `TaskSection` | Tasks grouped by Overdue / Due today / Due later |
| `TaskCard` | Title, due date chip (color-coded) |
| `BriefingHistory` | Modal showing past briefing summaries |
| `MessageBubble` | User (right-aligned) / Assistant (left-aligned) |
| `ConfirmActionBanner` | Inline confirm/cancel for calendar proposals |
| `ServiceConnectionPrompt` | First-login prompt to connect services |
| `SettingsPage` | Service connection status, reconnect/disconnect buttons |

---

## 12. Security Considerations

| Concern | Mitigation |
|---------|-----------|
| Password storage | bcrypt with cost factor 12 |
| JWT secret | Loaded from `JWT_SECRET_KEY` env var; RS256 or HS256 |
| OAuth tokens | AES-encrypted (Fernet) with `CREDENTIAL_ENCRYPTION_KEY` |
| User data isolation | Every DB query includes `WHERE user_id = ?` filter |
| CORS | Restricted to `CORS_ORIGINS` env var (localhost in dev) |
| Calendar writes | Require explicit confirmation — never triggered by pipeline |
| Email sending | Not implemented — drafts only |

---

## 13. Environment Variables

```bash
# Gemini
GEMINI_API_KEY=

# Google OAuth App Credentials (shared app, per-user tokens stored in DB)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Credential encryption
CREDENTIAL_ENCRYPTION_KEY=        # 32-byte Fernet key (base64)

# App
DATABASE_URL=sqlite:///./dailybrief.db
CORS_ORIGINS=http://localhost:5173

# Calendar
GOOGLE_CALENDAR_ID=primary
```

---

## 14. Build Order & Milestones

### Milestone 1 — Three read-only agents + static briefing
Agents fetch + classify data. Coordinator synthesizes. UI renders briefing (no auth yet, single user).  
**Demo:** Run briefing endpoint, see classified emails/events/tasks in the UI.

### Milestone 2 — SQLite persistence + briefing history
Each run saved to DB. History list + detail view in UI.  
**Demo:** Run twice, see both in history. Click one to view.

### Milestone 3 — Date-aware task classification
Notes Agent uses real dates. UI shows Overdue (red) / Due today (amber) / Due later chips.  
**Demo:** Task with yesterday's due date appears as Overdue in red.

### Milestone 4 — Draft email generation
"Draft Reply" button calls `/api/actions/draft`, renders editable inline draft.  
**Demo:** Click Draft Reply on urgent email → editable AI draft appears.

### Milestone 5 — Chat panel
Right panel live with Gemini-powered Q&A over in-memory briefing session.  
**Demo:** Ask "What's my 2pm about?" → answer drawn from briefing data.

### Milestone 6 — Calendar write-back with confirmation
Chat/UI proposes slot → user confirms → event written to Google Calendar via MCP.  
**Demo:** "Schedule [task] for 3pm" → confirm → event appears in Google Calendar.

### Milestone 7 — Multi-user auth (final phase)
Signup/login, per-user OAuth, credential isolation, JWT-protected routes, settings page.  
**Demo:** Two users log in, each see their own briefings and credentials; no data leakage.
