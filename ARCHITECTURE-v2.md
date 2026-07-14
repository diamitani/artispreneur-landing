# Artispreneur v2 — Architecture & User Flows

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | Jul 12 | Landing page, 6 agents, tools section, basic pricing |
| v1.1 | Jul 13 | Navigation fix, all 8 pages cross-linked, logo |
| v1.2 | Jul 14 | Directory page (183 contacts), workspace dashboard, 8 course pages |
| v1.3 | Jul 14 | 16 courses (307 modules), curriculum agent, academy integration |
| **v2.0** | **Jul 14** | **Chat UI, signup flow, AWS backend, user onboarding, Hermes provisioning** |

---

## User Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     LANDING PAGE (NEW)                           │
│                                                                  │
│  ┌─────────────────────┐    ┌─────────────────────────────────┐ │
│  │    Hero + Chat UI    │    │     Marketing Sections          │ │
│  │                      │    │                                 │ │
│  │  "Your Music         │    │  Agents · Tools · Academy       │ │
│  │   Business OS"       │    │  Directory · Pricing · Blog     │ │
│  │                      │    │                                 │ │
│  │  ┌────────────────┐  │    │  [Sign Up]  [Try Chat]         │ │
│  │  │  Agent Chat    │  │    │                                 │ │
│  │  │  ───────────── │  │    │                                 │ │
│  │  │  Ask anything  │  │    │                                 │ │
│  │  │  about music   │  │    │                                 │ │
│  │  │  business...   │  │    │                                 │ │
│  │  │                │  │    │                                 │ │
│  │  │  [Send]        │  │    │                                 │ │
│  │  └────────────────┘  │    │                                 │ │
│  └─────────────────────┘    └─────────────────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                     SIGNUP FLOW                                  │
│                                                                  │
│  Step 1: Choose Plan                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │  Free    │  │  BYOK    │  │  Pro     │                      │
│  │  $0/mo   │  │  $0/mo   │  │  $29/mo  │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │              │              │                            │
│       ▼              ▼              ▼                            │
│  Step 2: Create Account                                          │
│  ┌──────────────────────────────────────────┐                   │
│  │  Email: _______  Password: _______        │                   │
│  │  Name: ________  Artist/Business Name     │                   │
│  │  [Sign up with Google]                    │                   │
│  │  (BYOK: Paste API key)                    │                   │
│  └──────────────────────────────────────────┘                   │
│       │                                                          │
│       ▼                                                          │
│  Step 3: Onboarding                                              │
│  ┌──────────────────────────────────────────┐                   │
│  │  Tell us about your music:               │                   │
│  │  Genre: ______  PRO: ASCAP/BMI/SESAC     │                   │
│  │  Goals: ______  Current stage: ______    │                   │
│  │                                          │                   │
│  │  → This builds your soul.md              │                   │
│  └──────────────────────────────────────────┘                   │
│       │                                                          │
│       ▼                                                          │
│  Step 4: Provisioning                                            │
│  ┌──────────────────────────────────────────┐                   │
│  │  ⏳ Setting up your workspace...          │                   │
│  │  • Creating agent instance                │                   │
│  │  • Installing Hermes Agent                │                   │
│  │  • Building ROSTR PAL compiler            │                   │
│  │  • Writing soul.md from onboarding        │                   │
│  │  • Connecting Google Drive (optional)     │                   │
│  │  • Setting up Signal bridge (optional)    │                   │
│  │                                          │                   │
│  │  [Done! Go to Dashboard →]               │                   │
│  └──────────────────────────────────────────┘                   │
│       │                                                          │
│       ▼                                                          │
│  DASHBOARD (authenticated)                                       │
│  /dashboard                                                      │
│  ┌──────────────────────────────────────────┐                   │
│  │  Sidebar         │  Main Content         │                   │
│  │  ⌂ Home          │                       │                   │
│  │  ◈ Agents        │  ┌─────────────────┐  │                   │
│  │  📁 Outputs      │  │  Agent Chat     │  │                   │
│  │  ◎ Projects      │  │                 │  │                   │
│  │  📚 Knowledge     │  │  "Hey PRO Agent │  │                   │
│  │  ◉ Directory     │  │   register my   │  │                   │
│  │  🎓 Academy      │  │   new song"     │  │                   │
│  │  👤 Profile      │  │                 │  │                   │
│  │  ⚙ Settings      │  └─────────────────┘  │                   │
│  └──────────────────┴───────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VERCEL (Frontend)                         │
│                                                                  │
│  artispreneur.com                                                │
│  ├── / (landing + chat UI)                                       │
│  ├── /signup (onboarding flow)                                   │
│  ├── /dashboard (authenticated workspace)                        │
│  ├── /academy, /directory, /pricing, etc.                        │
│  └── /api/* (Next.js API routes → backend proxy)                 │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                    ┌──────┴──────┐
                    │  SUPABASE   │
                    │  Auth + DB  │
                    │  Real-time  │
                    └──────┬──────┘
                           │
┌──────────────────────────┴──────────────────────────────────────┐
│                    AWS (Backend)                                  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                  API Gateway / Lambda                     │    │
│  │  POST /provision-user   →  Creates EC2 + Hermes         │    │
│  │  POST /agent/chat       →  Routes to user's agent       │    │
│  │  GET  /agent/status     →  Agent health + session       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              EC2 — Per-User Agent Instances              │    │
│  │                                                          │    │
│  │  /home/artispreneur/users/{user_id}/                     │    │
│  │  ├── hermes-agent/          (Hermes binary)              │    │
│  │  ├── .rostr/                                            │    │
│  │  │   ├── state/session.json                              │    │
│  │  │   ├── state/memory.jsonl                              │    │
│  │  │   ├── state/decisions.md                              │    │
│  │  │   ├── state/learnings.jsonl                           │    │
│  │  │   └── soul.md               (PAL-compiled context)    │    │
│  │  ├── skills/                   (user's installed skills) │    │
│  │  ├── outputs/                  (EPKs, contracts, etc)     │    │
│  │  └── config.yaml              (LLM provider + API keys)  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Shared Services                        │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │    │
│  │  │  Redis   │  │  S3/R2   │  │  Signal  │  │ Vector  │ │    │
│  │  │ (cache)  │  │ (files)  │  │  Bridge  │  │  (RAG)  │ │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

---

## Signup → Provisioning Pipeline

```
1. User submits signup form (plan, email, password, onboarding answers)
2. Supabase Auth creates user + stores profile in `workspace_users`
3. Webhook fires → POST /provision-user (AWS Lambda)
4. Lambda:
   a. Creates EC2 micro instance (or reuses shared instance pool)
   b. Runs cloud-init script:
      - apt-get install hermes-agent
      - hermes setup --profile artispreneur
      - writes config.yaml (LLM provider from user's plan)
      - writes soul.md from onboarding answers
      - starts hermes agent daemon
   c. Updates `agent_sessions` table: status = 'active'
   d. Returns agent endpoint URL
5. Frontend polls until agent_ready = true
6. Redirect to /dashboard with ws:// connection to agent
```

---

## Hermes Agent v2 Config (per user)

```yaml
# /home/artispreneur/users/{id}/config.yaml
agent:
  name: "{artist_name}'s Artispreneur Agent"
  version: "2.0"

providers:
  primary:
    provider: "{free: google, byok: user_choice, pro: managed}"
    model: "{free: gemini-2.5-flash, byok: user_model, pro: claude-sonnet-4}"

rostr:
  pal:
    enabled: true
    soul_path: ".rostr/soul.md"
  ragdal:
    enabled: true
    tiers: [1.0, 0.75, 0.40]
  npao:
    phases: [pred, design, development, deployment, debugging]
    agents: [pro, distribution, licensing, legal, finance, manager]

tools:
  - web_search
  - file_system
  - code_execution
  - google_drive
  - signal_messaging
  - supabase_db

integrations:
  google_drive: "{user_connected}"
  signal_phone: "{user_phone}"
```

---

## Dashboard Wireframe

```
┌─────────────────────────────────────────────────────────────────┐
│  [Logo]  Dashboard  Agents  Outputs  Knowledge  [Profile] [⚙]  │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                      │
│  SIDEBAR │  ┌──────────────────────────────────────────────┐   │
│          │  │         AGENT CHAT                           │   │
│  ⌂ Home  │  │                                              │   │
│  ◈ Agents│  │  ┌────────────────────────────────────────┐  │   │
│  📁 Out  │  │  │                                        │  │   │
│  ◎ Proj  │  │  │  Agent: Hey! I see you have a new     │  │   │
│  📚 Know  │  │  │  single ready. Want me to:            │  │   │
│  ◉ Dir   │  │  │  1. Register with BMI                 │  │   │
│  🎓 Acad  │  │  │  2. Submit to playlists               │  │   │
│  👤 Prof  │  │  │  3. Create splitsheets                │  │   │
│  ⚙ Set   │  │  │                                        │  │   │
│          │  │  └────────────────────────────────────────┘  │   │
│          │  │  ┌────────────────────────────────────────┐  │   │
│  [Plan]  │  │  │  Type a message...              [Send] │  │   │
│  Upgrade │  │  └────────────────────────────────────────┘  │   │
│          │  └──────────────────────────────────────────────┘   │
│          │                                                      │
│          │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │
│          │  │ PRO Agent   │ │ Dist Agent  │ │ Legal Agent │   │
│          │  │ ✓ Active    │ │ ✓ Active    │ │ ⚙ Running   │   │
│          │  └─────────────┘ └─────────────┘ └─────────────┘   │
│          │                                                      │
│          │  ┌──────────────────────────────────────────────┐   │
│          │  │  Recent Outputs                               │   │
│          │  │  📄 LLC_Agreement_v2.pdf  (2 days ago)       │   │
│          │  │  🎵 Metadata_Export.xlsx   (3 days ago)      │   │
│          │  └──────────────────────────────────────────────┘   │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## Cost Model v2

| Component | Free Tier | BYOK | Pro ($29/mo) |
|-----------|-----------|------|--------------|
| LLM | Gemini Flash credits | User's API key | Managed Claude Sonnet 4 |
| Agent instance | Shared EC2 (100 users/vm) | Shared | Dedicated t3.micro |
| Provisioning time | ~30 seconds | ~30 seconds | ~15 seconds |
| Messages/month | 500 | Unlimited | Unlimited |
| Outputs/month | 25 | Unlimited | Unlimited |
| Drive sync | No | Yes | Yes |
| Signal/Wire | No | Yes | Yes |
| Support | Community | Email | Priority chat |
