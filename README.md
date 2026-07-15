<div align="center">

# ✦ Auralis

### AI Creative Studio — turn any product URL into a full marketing campaign.

Generate on-brand ad copy, images, videos, and UGC scripts from a single product
link or a few manual details. Premium dark UI, modular architecture, production-ready.

</div>

---

## ✨ What it does

Paste a product URL (or enter details by hand) and Auralis:

1. **Scrapes** the page (Playwright + BeautifulSoup) — title, images, logo, features, pricing, reviews, brand colors.
2. **Analyses** the product into a marketing brief — brand voice, persona, pain points, angles, hooks, USP.
3. **Generates** creative across surfaces:
   - **Copy** — Facebook / Instagram / Google / LinkedIn / Twitter / landing / email, in Luxury / Professional / Friendly / Minimal tones.
   - **Images** — square / portrait / landscape / story / carousel / poster / lifestyle.
   - **Video** — storyboard, script, voiceover, captions, transitions (15s / 30s / 60s / Reels / Shorts / Stories).
   - **UGC** — creator scripts, camera directions, scene breakdown, B-roll, hooks.
4. **Scores** every creative (hook strength, readability, brand consistency, CTA quality, conversion potential) with improvement tips.
5. **Remembers your brand** — logo, colors, fonts, voice — and applies it to every generation automatically.
6. **Exports** PNG / JPG / MP4 / PDF campaign summary / ZIP package, with full export history.

> **Runs with zero setup.** With no API keys the backend runs in **mock mode**, returning realistic sample content (and on-brand template images) for every generator so the entire product is explorable offline. Add keys to switch each surface to live generation:
>
> | Surface | Provider | Env key |
> |---|---|---|
> | Copy · analysis · UGC · scoring · video scripts | **OpenAI GPT** | `OPENAI_API_KEY` |
> | Product images (edits your real product photo) | **Google Nano Banana** (Gemini 2.5 Flash Image) | `GOOGLE_API_KEY` |
> | Showcase video (talking-head presenter) | **HeyGen** avatar | `HEYGEN_API_KEY` |
>
> Fill them in `.env` (see `.env.example`). Keys: [platform.openai.com/api-keys](https://platform.openai.com/api-keys) · [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (must start `AIza…`, billing on) · [app.heygen.com](https://app.heygen.com) → Settings → API.
>
> **Auto Campaign** (`/campaign`): paste a product URL → it scrapes it, creates professional product images, and drafts a video script → **you review/approve** → it renders a presenter video.

---

## 🧱 Architecture

```
┌────────────┐   /api    ┌──────────────┐   Celery/Redis   ┌────────────┐
│  Next.js   │ ────────▶ │   FastAPI    │ ───────────────▶ │  Worker    │
│  (App Rtr) │           │  (services)  │                  │ (scrape/AI)│
└────────────┘           └──────┬───────┘                  └─────┬──────┘
      ▲   nginx (:80)           │ SQLAlchemy (async)              │
      │                         ▼                                 ▼
      └──────────────────  PostgreSQL 16   ◀───────────────  Local storage
```

| Layer      | Stack |
|------------|-------|
| Frontend   | Next.js 15 (App Router) · TypeScript · Tailwind · shadcn/ui · Framer Motion · Lucide · Recharts · TanStack Query |
| Backend    | FastAPI · SQLAlchemy 2 (async) · Pydantic v2 · PostgreSQL · Redis · Celery · Playwright · BeautifulSoup · OpenAI (GPT) · Google GenAI (Nano Banana + Imagen) · HeyGen (avatar video) |
| Infra      | Docker · Docker Compose · nginx |

Each feature has its own **service layer**; heavy work (scraping, AI generation, exports) runs as **Celery tasks**. Storage is behind an interface (`LocalStorage`) so S3 / R2 is a drop-in later. No auth/billing yet — the app opens straight into the dashboard for a single local user, and the architecture leaves clean seams to add them.

```
backend/app/
  api/       routes + deps
  services/  one module per feature
  models/    SQLAlchemy tables
  schemas/   Pydantic contracts
  prompts/   AI prompt templates
  workers/   Celery app + tasks
  storage/   pluggable asset storage
  core/      config, logging
  database/  engine + session

frontend/src/
  app/               routes (landing + dashboard group)
  components/        ui · layout · landing · dashboard · generator · charts · cards
  lib/               api client · types · utils
  hooks/             data hooks (TanStack Query)
```

---

## 🚀 Run it

### Docker (recommended)

```bash
cp .env.example .env          # tweak if you like; defaults just work
docker compose up --build
```

- App:      http://localhost         (nginx → frontend + /api)
- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

Add live AI: set `OPENAI_API_KEY=` and/or `GOOGLE_API_KEY=` in `.env`, then `docker compose up -d --build backend worker`.

### Local dev (without Docker)

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # optional, only for live scraping
export DATABASE_URL=postgresql+asyncpg://auralis:auralis@localhost:5432/auralis
export REDIS_URL=redis://localhost:6379/0
uvicorn app.main:app --reload
# separate shell:
celery -A app.workers.celery_app.celery_app worker --loglevel=info
```

**Frontend**
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

---

## 🗄️ Data model

`projects` · `product_data` · `brand_memory` · `generated_copy` · `generated_images` ·
`generated_videos` · `creative_scores` · `exports` · `analytics_events` · `settings`

Relationships are project-scoped with indexes on foreign keys and creation time. Tables are created on startup for the MVP; Alembic is wired for real migrations.

---

## 🎨 Design

Original premium identity — dark theme, glassmorphism, aurora gradients, large rounded
cards, soft shadows, generous spacing, Framer Motion throughout (page transitions, hover,
animated gradients, skeleton shimmer, animated numbers). Fully responsive, accessible,
built for an Apple-level finish. It does not copy any existing product's branding.

---

## 🛣️ Built to grow

The modular seams mean **auth, billing, credits, team workspaces, and cloud storage**
can be layered in without refactoring the core. This is V1 (MVP) — intentionally scoped
to the creative engine.
