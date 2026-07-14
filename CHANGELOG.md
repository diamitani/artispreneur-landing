# Artispreneur — Version History

## v2.1 — Unified Dashboard (Jul 14, 2026)
- **Dashboard rebuilt** — all features integrated under one sidebar
- **Agent chat** in dashboard home tab
- **Academy embedded** in dashboard — 16 courses, filterable by category
- **Directory embedded** — 6 categories, live search, 183 contacts
- **Agent locking** on Free plan — Licensing & Finance locked behind BYOK/Pro
- **Settings** tab — profile, API keys, integrations
- **Knowledge Base** tab — soul.md preview
- **Outputs** tab — generated files with draft/final tags

### Files changed
- `workspace.html` — full rewrite with embedded academy, directory, agents, chat

---

## v2.0 — Agent Chat + Signup Flow (Jul 14, 2026)
- **Landing page redesigned** with embedded chat UI (live demo)
- **Signup flow** — 4-step onboarding: Plan → Account → Setup → Provisioning
- **Architecture v2** — AWS provisioning pipeline, per-user EC2 Hermes instances
- **ROSTR PAL compiler** — soul.md auto-generated from onboarding
- **Pricing → signup** clickthrough (no longer dead contact form)
- **Version tracking** — this CHANGELOG.md

### Files changed
- `index.html` — redesigned with chat widget
- `signup.html` — new 4-step signup flow
- `ARCHITECTURE-v2.md` — full system design
- `CHANGELOG.md` — this file

---

## v1.3 — Full Academy Integration (Jul 14, 2026)
- **16 courses, 307 modules** — generated from Academy spreadsheet
- **Curriculum instructor agent** (`build_all_courses.py`) — reads .xlsx, generates HTML
- All 16 courses have full lesson breakdowns with module content
- Academy page updated with filtering by category
- Course detail pages for every course

### Files changed
- `academy.html` — updated with 16 courses
- `courses/*.html` — 16 course detail pages
- `build_all_courses.py` — spreadsheet → HTML agent
- `build_courses.py` — courses.ts → HTML agent

---

## v1.2 — Directory + Workspace + Courses (Jul 14, 2026)
- **Directory page** — 6 categories, 183 contacts, live search
- **Workspace page** — agent dashboard, 6 agent cards, outputs, activity, soul.md preview
- **8 course pages** — from courses.ts, 57 modules with full content
- Fixed course links (were 404ing on academy site)
- Backend architecture doc tightened (Supabase-only, RLS, unified schema)

### Files changed
- `directory.html` — new
- `workspace.html` — new
- `courses/*.html` — 8 course detail pages
- `BACKEND-ARCHITECTURE.md` — tightened
- `academy.html` — updated links

---

## v1.1 — Navigation + Logo Fix (Jul 13, 2026)
- **Logo** added to all 9 pages (navbar + footer)
- **Navigation unified** — 8 links on every page
- Privacy and Terms pages fixed (had stripped navs)
- Directory link added to all nav bars

### Files changed
- All 9 `.html` files — logo + nav updates
- `logo.png` — added (113KB)

---

## v1.0 — Initial Launch (Jul 12, 2026)
- **Landing page** with hero, 6 agents, tools section
- **7 subpages**: About, Pricing, Academy, Contact, Blog, Privacy, Terms
- Dark theme, gold accents, Playfair Display + Inter fonts
- Deployed to Vercel: artispreneur-landing.vercel.app

### Files created
- `index.html`, `about.html`, `pricing.html`, `academy.html`
- `contact.html`, `blog.html`, `privacy.html`, `terms.html`
- `SITEMAP.md`, `BACKEND-ARCHITECTURE.md`, `ONE-SHEETER.html`

### Tech stack
- Static HTML + CSS + vanilla JS
- Vercel hosting
- GitHub (diamitani/artispreneur-landing)
- Cross-linked with academy-build.vercel.app, directory-build.vercel.app
