# Artispreneur — Backend Architecture (Tightened)

## Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Auth** | Supabase Auth | OAuth (Google, Apple, email), Row-Level Security, free tier (50K users) |
| **Database** | Supabase PostgreSQL | One database, RLS-isolated tenants, real-time subscriptions |
| **Storage** | Supabase Storage + Cloudflare R2 | User outputs, EPKs, contracts; R2 for public assets |
| **Vector DB** | pgvector (Supabase extension) | RAG knowledge base — same DB, no separate service |
| **Agents** | Hermes Agent (Nous Research) | Per-user agent instances, ROSTR framework, tool orchestration |
| **Messaging** | Signal CLI bridge + Matrix bridge | Encrypted command surface, optional BYO-device |
| **Frontend** | Next.js 15 + Tailwind | React Server Components, Turbopack, deployed on Vercel |
| **LLM** | Gemini (free credits) / BYOK | OpenAI, Anthropic, Groq, Ollama — user chooses |

## Single Database, Unified Schema

All three apps (Landing, Academy, Connect/Workspace) share one Supabase project. No separate AWS RDS, no multi-database sprawl.

```
┌────────────────────────────────────────────┐
│              Supabase Project               │
│                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │  Auth    │ │  Storage  │ │  pgvector     ││
│  │  (users) │ │  (files)  │ │  (embeddings) ││
│  └──────────┘ └──────────┘ └──────────────┘│
│                                             │
│  ┌──────────────────────────────────────────┐│
│  │           PostgreSQL (RLS)               ││
│  │                                          ││
│  │  auth.users                              ││
│  │  ├── academy_profiles                    ││
│  │  ├── workspace_users (NEW)               ││
│  │  │                                       ││
│  │  academy schema:                         ││
│  │  ├── courses + modules                   ││
│  │  ├── course_progress                     ││
│  │  ├── certificates                        ││
│  │  ├── media_resources                     ││
│  │  │                                       ││
│  │  workspace schema (NEW):                 ││
│  │  ├── agent_sessions                      ││
│  │  ├── agent_actions                       ││
│  │  ├── contacts (directory)                ││
│  │  ├── music_catalog                       ││
│  │  ├── splits                              ││
│  │  ├── outputs                             ││
│  │  ├── soul_docs                           ││
│  │  └── user_events (cross-app)             ││
│  └──────────────────────────────────────────┘│
└────────────────────────────────────────────┘
```

## Core Schema

### Profiles & Auth (existing)

```sql
auth.users  -- managed by Supabase Auth

academy_profiles (
  id UUID PK,
  user_id UUID FK → auth.users UNIQUE,
  first_name, last_name TEXT,
  email TEXT,
  user_type TEXT CHECK (producer|artist|manager|label|brand|other),
  registered_app_id TEXT DEFAULT 'academy',
  current_app_id TEXT DEFAULT 'academy',
  avatar_url TEXT,
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own
```

### Workspace Tables (NEW)

```sql
-- User workspace metadata
workspace_users (
  id UUID PK,
  user_id UUID FK → auth.users UNIQUE,
  plan TEXT DEFAULT 'free' CHECK (free|byok|pro),
  llm_provider TEXT,          -- openai|anthropic|groq|ollama|gemini
  llm_key_encrypted TEXT,     -- AES-256 encrypted at rest
  google_drive_linked BOOLEAN DEFAULT false,
  signal_phone TEXT,          -- for Signal bridge
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Agent sessions — one per user per agent type
agent_sessions (
  id UUID PK,
  user_id UUID FK → auth.users,
  agent_type TEXT CHECK (pro|distribution|licensing|legal|finance|manager),
  status TEXT DEFAULT 'idle' CHECK (idle|running|paused|error),
  session_data JSONB DEFAULT '{}',  -- Hermes agent state
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Agent action log
agent_actions (
  id UUID PK,
  session_id UUID FK → agent_sessions,
  user_id UUID FK → auth.users,
  agent_type TEXT,
  action_type TEXT,            -- register_pro|distribute|license|llc|tax|plan…
  input JSONB DEFAULT '{}',
  output JSONB DEFAULT '{}',
  status TEXT DEFAULT 'pending' CHECK (pending|running|success|failed),
  created_at, completed_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Artist's project context (soul.md)
soul_docs (
  id UUID PK,
  user_id UUID FK → auth.users UNIQUE,
  content TEXT NOT NULL DEFAULT '# Soul\n\nArtist: ...',
  version INTEGER DEFAULT 1,
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Industry contacts directory
contacts (
  id UUID PK,
  user_id UUID FK → auth.users,
  name TEXT NOT NULL,
  type TEXT CHECK (artist|label|supervisor|venue|radio|blog|podcast|press|other),
  email TEXT, phone TEXT, url TEXT,
  location TEXT, notes TEXT,
  tags TEXT[] DEFAULT '{}',
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Music catalog
music_catalog (
  id UUID PK,
  user_id UUID FK → auth.users,
  title TEXT NOT NULL,
  isrc TEXT, iswc TEXT,
  genre TEXT, release_date DATE,
  metadata JSONB DEFAULT '{}',
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Splits / ownership
splits (
  id UUID PK,
  catalog_id UUID FK → music_catalog,
  user_id UUID FK → auth.users,
  collaborator_name TEXT,
  collaborator_pro TEXT,       -- PRO affiliation
  percentage DECIMAL CHECK (percentage > 0 AND percentage <= 100),
  role TEXT,                   -- writer|producer|feature|publisher
  created_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Output files (EPKs, contracts, etc.)
outputs (
  id UUID PK,
  user_id UUID FK → auth.users,
  type TEXT CHECK (epk|contract|analysis|report|template|other),
  title TEXT NOT NULL,
  file_path TEXT,              -- Supabase Storage path
  drive_link TEXT,             -- optional Google Drive link
  version INTEGER DEFAULT 1,
  status TEXT DEFAULT 'draft' CHECK (draft|review|final),
  created_at, updated_at TIMESTAMPTZ
) RLS: user can CRUD own

-- Cross-app events
user_events (
  id UUID PK,
  user_id UUID FK → auth.users,
  app_id TEXT NOT NULL,        -- academy|workspace|directory
  event_type TEXT,             -- login|course_start|agent_action|output_generated…
  event_data JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ
) RLS: user can CRUD own, service_role can read all
```

## ROSTR Agent State (per-user files)

Each user gets a `.rostr/` directory on Supabase Storage:

```
/users/{user_id}/.rostr/
├── state/
│   ├── session.json      # Current conversation context
│   ├── memory.jsonl      # Append-only interaction log
│   ├── decisions.md      # Agent decision rationale
│   └── learnings.jsonl   # Pattern discoveries
├── soul.md               # Artist project state (synced to DB)
├── skills/               # Installed agent skills
└── config.yaml           # LLM provider + API key prefs
```

## RLS: Zero Cross-Tenant Leakage

Every table is locked to `auth.uid() = user_id`. No user can ever read another user's data. The `service_role` key (used by the Hermes agent backend) can access all tables — but it runs server-side, never exposed to clients.

## LLM Flow

```
User command → Supabase realtime → Hermes Agent instance
  → ROSTR PAL compiler (intent parse)
  → NPAO router (which agent, what phase)
  → RAG DAL (query pgvector knowledge base)
  → Agent executes (tool calls, API actions)
  → Output saved to Supabase Storage + DB
  → Response delivered via Supabase realtime / Signal / email
```

## Deployment

| Layer | Target | Cost |
|-------|--------|------|
| Supabase | Cloud (supabase.com) | Free tier (500MB DB, 50K users) |
| Hermes Agent | Oracle Cloud free ARM (4 OCPUs, 24GB) | $0 |
| Frontend | Vercel | Free tier |
| Assets | Cloudflare R2 | Free tier (10GB) |
| Vector | pgvector on Supabase | Included |

**Total infrastructure cost at launch: $0/month.**
