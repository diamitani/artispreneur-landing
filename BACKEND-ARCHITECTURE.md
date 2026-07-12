# Artispreneur — Backend Architecture

## Stack Overview

1. **Hermes Agent** (Nous Research) — AI agent runtime
2. **ROSTR Framework** — structured agent orchestration (PAL + NPAO + RAG DAL)
3. **Signal / Wire** — encrypted messaging command surface

---

## Architecture

```
artispreneur.com (Next.js 15)
        │
        ▼
    API Gateway
    ├── NextAuth
    ├── Rate Limiter
    └── Tenant Router
        │
        ▼
    Hermes Agent Runtime (per user)
    └── ROSTR Framework
        ├── PAL Compiler → intent parsing
        ├── NPAO Orchestrator → phase routing
        ├── RAG DAL → knowledge retrieval
        └── Rostr Hub → state + soul.md
            │
            ├── PRO Agent
            ├── Distribution Agent
            ├── Licensing Agent
            ├── Legal Agent
            ├── Finance Agent
            └── Manager Agent
        │
        ▼
    Data Layer
    ├── PostgreSQL (users, catalog)
    ├── Supabase (auth, realtime)
    ├── Cloudflare R2 (files, outputs)
    ├── Qdrant (vector DB for RAG)
    └── Redis (cache, queues)
```

---

## Messaging Flow (Signal/Wire)

```
User → Signal/Wire → Bridge Service → PAL Compiler → NPAO Router → Agent → Response via Signal
```

## LLM Strategy

| Tier | Provider | Model |
|------|----------|-------|
| Free | Gemini (credits) | Flash 2.5 |
| BYOK | User's choice | OpenAI, Anthropic, Groq, Ollama |
| Pro | Managed | Same as above + priority |

## Per-User State

```
/user/{id}/.rostr/
├── state/session.json
├── state/memory.jsonl
├── state/decisions.md
├── state/learnings.jsonl
├── soul.md
└── config.yaml
```

## Deployment

- **Frontend:** Vercel
- **Backend:** Oracle Cloud free ARM (4 OCPUs, 24GB) → AWS Fargate at scale
- **Auth:** Supabase free tier
- **Storage:** Cloudflare R2 (10GB free)
- **Vector DB:** Qdrant (on Oracle instance)

## Cost Model

| | Free | BYOK | Pro ($29/mo) |
|---|---|---|---|
| LLM | Gemini credits | User keys | Managed compute |
| Messages | 1,000/mo | Unlimited | Unlimited |
| Outputs | 50/mo | Unlimited | Unlimited |
| Drive Sync | No | Yes | Yes |
| Skills Mkt | Browse | Full | Full |
