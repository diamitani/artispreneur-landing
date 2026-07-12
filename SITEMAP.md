# Artispreneur.com — Sitemap

## Public Pages

| Path | Page | Description |
|------|------|-------------|
| `/` | Landing Page | Hero, agents, tools, pricing, CTA |
| `/about` | About | Mission, team, story |
| `/pricing` | Pricing | Free, BYOK, Pro tiers |
| `/blog` | Blog | Music industry insights, tutorials |
| `/contact` | Contact | Form, social links, support |
| `/privacy` | Privacy Policy | Legal |
| `/terms` | Terms of Service | Legal |

## Authentication

| Path | Page |
|------|------|
| `/signin` | Login (email, OAuth) |
| `/signup` | Register (email, Google, Apple) |
| `/forgot-password` | Password reset |

## Dashboard (authenticated)

| Path | Page |
|------|------|
| `/dashboard` | Home — agent status, roadmap, activity |
| `/dashboard/profile` | Public artist profile — bio, media, discography |
| `/dashboard/settings` | API keys, email, name, delete account |
| `/dashboard/workspace` | Core agentic workspace |
| `/dashboard/workspace/agents` | Agent hub — all 6 agents |
| `/dashboard/workspace/agents/[id]` | Individual agent UI |
| `/dashboard/workspace/skills` | Skills marketplace |
| `/dashboard/workspace/prompts` | Prompt library |
| `/dashboard/workspace/outputs` | Output management |
| `/dashboard/workspace/projects` | Project boards |
| `/dashboard/knowledge` | Knowledge base |
| `/dashboard/knowledge/contacts` | Contact directory |
| `/dashboard/knowledge/catalog` | Music catalog |
| `/dashboard/directory` | Industry directory |
| `/dashboard/directory/playlists` | Playlist directory |
| `/dashboard/directory/venues` | Venues directory |
| `/dashboard/directory/studios` | Studios directory |
| `/dashboard/academy` | Learning hub |
| `/dashboard/academy/courses` | Courses |
| `/dashboard/academy/templates` | Templates |

## API Routes

| Path | Purpose |
|------|---------|
| `/api/auth/*` | NextAuth endpoints |
| `/api/agents/*` | Agent orchestration |
| `/api/knowledge/*` | RAG queries, document CRUD |
| `/api/directory/*` | Directory listing |
| `/api/outputs/*` | File management |
| `/api/webhooks/*` | Signal/Wire intake, DSP callbacks |

## Navigation

**Top Nav (public):** Home · Agents · Tools · How It Works · Pricing · Stack

**Sidebar (dashboard):** Home · Workspace · Knowledge Base · Directory · Academy · Profile · Settings

**Footer:** About · Blog · Contact · Privacy · Terms
