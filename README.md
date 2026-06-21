# DailyBrief

An AI-powered morning briefing app that pulls together your Gmail, Google Calendar, and Notion tasks into a single structured daily brief — with a chat panel for follow-up questions and one-click actions.

![Stack](https://img.shields.io/badge/backend-FastAPI%20%2B%20Python%203.11-blue)
![Stack](https://img.shields.io/badge/frontend-React%2018%20%2B%20Vite%207-61dafb)
![Stack](https://img.shields.io/badge/AI-Gemini-orange)

---

## What it does

- **Morning briefing** — one click generates a full summary of your day: classified emails, calendar events with conflict detection, and Notion tasks sorted by urgency
- **AI focus suggestion** — Gemini synthesizes everything into a 2–4 sentence "here's what to tackle first today"
- **Cross-referencing** — automatically links related items (e.g. an email about a meeting happening today)
- **Draft email replies** — generate an editable suggested reply for any urgent email; never auto-sends
- **Calendar scheduling** — propose a time slot for overdue/due-today tasks; only writes to Google Calendar after you explicitly confirm
- **Chat panel** — ask follow-up questions like "what's my 2pm about?" or "draft a reply to Anjali" using the already-gathered session data
- **Briefing history** — every run is saved to SQLite so you can look back at past days
- **Multi-user** — each person connects their own accounts; data is fully isolated

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11, FastAPI 0.115, Uvicorn |
| Database | SQLite via SQLAlchemy 2.0 (async) + aiosqlite |
| AI | Google Gemini (`google-genai` SDK) |
| Auth | JWT (`python-jose`), bcrypt passwords, Fernet token encryption |
| External APIs | Gmail REST API, Google Calendar REST API, Notion REST API |
| Frontend | React 18, Vite 7, TypeScript (strict), Tailwind CSS 3 |
| State | Zustand (auth + briefing stores) |
| Data fetching | TanStack React Query v5, Axios |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- A Google Cloud project with the **Gmail API** and **Google Calendar API** enabled
- A Google OAuth 2.0 client (Web application type) with `http://localhost:8000/auth/google/callback` as an authorized redirect URI
- A [Gemini API key](https://aistudio.google.com/app/apikey)
- A [Notion internal integration](https://www.notion.so/my-integrations) token

---

## Running the project

### 1. Clone and configure

```bash
git clone <repo-url>
cd dailybrief
copy backend\.env.example backend\.env
```

Open `backend\.env` and fill in your keys (see [Environment variables](#environment-variables) below).

---

### 2. Backend

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload --port 8000
```

The API is now running at **http://localhost:8000**  
Interactive docs: **http://localhost:8000/docs**

---

### 3. Frontend

Open a second terminal:

```bash
cd frontend

# Install dependencies (first run only)
npm install

# Start the dev server
npm run dev
```

The app is now running at **http://localhost:5173**

---

### 4. First-time setup in the browser

1. Go to **http://localhost:5173** and create an account
2. Click **Connect** to link Gmail + Google Calendar via Google OAuth
3. Go to **Settings** (⚙ icon on the dashboard) and paste your Notion integration token and database ID
4. Click **Run Briefing** — you're good to go

---

### Other useful commands

```bash
# Backend — run without auto-reload (production-like)
uvicorn main:app --port 8000

# Frontend — production build
npm run build

# Frontend — preview production build locally
npm run preview

# Frontend — lint (zero warnings policy)
npm run lint
```

---

## Environment variables

Copy `backend/.env.example` to `backend/.env` and fill in:

```env
# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Google OAuth (shared app credentials)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback

# JWT signing
JWT_SECRET_KEY=a-long-random-secret-string
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# Fernet key for encrypting stored OAuth tokens
# Generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
CREDENTIAL_ENCRYPTION_KEY=your_fernet_key

# Database (default is local SQLite)
DATABASE_URL=sqlite+aiosqlite:///./dailybrief.db

# CORS
CORS_ORIGINS=http://localhost:5173
```

---

## Connecting your services

After signing up and logging in:

1. **Gmail + Google Calendar** — click **Connect** on the dashboard prompt or in Settings. You'll be redirected to Google's consent screen. Both services are connected in one OAuth flow.

2. **Notion** — go to Settings (`⚙` icon on the dashboard), enter:
   - Your integration token (`secret_xxx...`) from [notion.so/my-integrations](https://www.notion.so/my-integrations)
   - Your database ID — found in the Notion database URL, e.g. `notion.so/My-Tasks-**abc123...**`
   
   Make sure you've shared the database with your integration (Share → Invite → select your integration).

---

## Project structure

```
dailybrief/
├── start.bat                   # One-command dev launcher (Windows)
├── DESIGN.md                   # Full architecture & design reference
├── backend/
│   ├── main.py                 # App factory, router registration, CORS
│   ├── config.py               # pydantic-settings singleton
│   ├── database.py             # SQLAlchemy async engine + session
│   ├── agents/                 # LLM + deterministic data agents
│   │   ├── email_agent.py      # Gmail fetch + Gemini classification
│   │   ├── calendar_agent.py   # GCal fetch + conflict detection (no LLM)
│   │   ├── notes_agent.py      # Notion fetch + date classification (no LLM)
│   │   └── coordinator_agent.py# Cross-ref, synthesis, proposals
│   ├── pipeline/               # 6-stage briefing pipeline
│   │   ├── orchestrator.py     # Runs stages in order, handles partial failures
│   │   ├── session_store.py    # In-memory per-user session cache (24h TTL)
│   │   └── stages/             # stage1_gather → stage6_persist
│   ├── mcp/                    # Thin async wrappers around Google/Notion APIs
│   │   ├── gmail_client.py
│   │   ├── gcal_client.py
│   │   └── notion_client.py
│   ├── routers/                # FastAPI route handlers (thin — no business logic)
│   ├── services/               # Business logic (auth, Gemini, drafts, encryption)
│   ├── models/                 # SQLAlchemy ORM models (users, credentials, briefings)
│   ├── schemas/                # Pydantic v2 request/response models
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/                # Axios call functions per domain
        ├── store/              # Zustand global state (auth + briefing)
        ├── hooks/              # useBriefing, useChat
        ├── pages/              # LoginPage, SignupPage, DashboardPage, HistoryPage, SettingsPage
        ├── components/
        │   ├── layout/         # TwoColumnLayout, BriefingPanel, ChatPanel
        │   ├── briefing/       # EmailSection, CalendarSection, TaskSection, etc.
        │   ├── chat/           # MessageBubble, ChatInput, ConfirmActionBanner
        │   └── auth/           # LoginForm, SignupForm, ServiceConnectionPrompt
        └── types/              # TypeScript interfaces mirroring backend schemas
```

---

## How the pipeline works

Each briefing run executes 6 stages:

| Stage | What happens |
|---|---|
| 1 — Gather | Fetches raw data from Gmail, GCal, and Notion in parallel. Each source is isolated — one failing doesn't abort the rest. |
| 2 — Analyze | Email agent classifies emails via Gemini. Calendar agent detects conflicts/back-to-back (pure Python). Notes agent classifies tasks by due date (pure Python). |
| 3 — Cross-reference | Coordinator agent uses Gemini to find links across sources (e.g. email → meeting today). |
| 4 — Synthesize | Coordinator builds the full `Briefing` object and generates the focus suggestion. |
| 5 — Propose | Matches overdue/due-today tasks to free calendar slots. Proposals are stored in memory only — never written automatically. |
| 6 — Persist | Saves the briefing to SQLite and updates the in-memory session store. |

---

## Key design decisions

- **No LLM for deterministic work** — calendar conflict detection and task date classification are pure Python, not Gemini calls.
- **Calendar writes are confirmation-gated** — proposals are stored in the session only; the actual write to Google Calendar only happens when the user explicitly hits Confirm.
- **Per-user isolation at every layer** — all DB queries filter by `user_id`; MCP clients are instantiated fresh per pipeline run with that user's decrypted tokens; the session store is keyed by `user_id`.
- **Partial failure tolerance** — if one source (e.g. Notion) fails, the briefing runs with the remaining data and is flagged as `partial`.
- **Retry with server hint** — Gemini 429 responses include a `retryDelay` suggestion; the service reads and honours it instead of burning retries with fixed backoff.


