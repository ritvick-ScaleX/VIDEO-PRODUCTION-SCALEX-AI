# Deploying ScaleX AI to Railway

The repo is a **monorepo** with two deployable services plus two managed databases:

| Service    | Path        | Build            | Notes                                  |
| ---------- | ----------- | ---------------- | -------------------------------------- |
| `backend`  | `./backend` | `Dockerfile`     | FastAPI + Playwright, binds `$PORT`    |
| `frontend` | `./frontend`| `Dockerfile`     | Next.js standalone, binds `$PORT`      |
| Postgres   | plugin      | Railway managed  | app data                              |
| Redis      | plugin      | Railway managed  | queue (optional; inline works too)    |

---

## Option A — one command (Railway CLI)

```bash
npm i -g @railway/cli      # 1. install CLI
railway login              # 2. authenticate (opens browser)
bash deploy/railway.sh     # 3. provision + deploy everything
```

`deploy/railway.sh` creates the project, adds Postgres + Redis, both services, a
persistent volume for generated media, wires every variable, generates public
domains, and cross-links CORS + the API URL. AI keys are read from
`backend/.env` if present, otherwise you're prompted. It targets Railway CLI v4;
if a step's flags differ on your version it prints what to finish in the dashboard.

## Option B — GitHub auto-deploy (dashboard)

Best if you want **push-to-deploy**. After pushing this repo to GitHub:

1. **New Project → Deploy from GitHub repo** → pick `VIDEO-PRODUCTION-SCALEX-AI`.
2. **Add Postgres** and **Add Redis** (New → Database).
3. Create the **backend** service from the repo → Settings → **Root Directory = `backend`** (it auto-detects the Dockerfile). Add the variables below, then **Generate Domain**.
4. Create the **frontend** service from the same repo → **Root Directory = `frontend`**. Add its variables, **Generate Domain**.
5. Every `git push` now redeploys both.

---

## Environment variables

### backend
```
DATABASE_URL        = ${{Postgres.DATABASE_URL}}      # app converts to asyncpg automatically
REDIS_URL           = ${{Redis.REDIS_URL}}
RUN_MIGRATIONS_ON_START = true                        # create_all on boot (no Alembic step needed)
ENVIRONMENT         = production
VIDEO_ENGINE        = veo
STORAGE_BACKEND     = local
STORAGE_DIR         = /app/storage_data               # mount a Volume here to persist media
STORAGE_PUBLIC_URL  = https://<backend-domain>/static
CORS_ORIGINS        = https://<frontend-domain>        # plain comma-list is fine, not just JSON
OPENAI_API_KEY      = sk-...                            # blank → mock text
OPENAI_MODEL        = gpt-4o
GOOGLE_API_KEY      = ...                               # blank → mock images/video
VEO_MODEL           = veo-3.1-fast-generate-preview
VEO_RESOLUTION      = 1080p                             # 720p for cheaper vertical renders
```

### frontend  (`NEXT_PUBLIC_*` are baked at **build** time — set before deploying)
```
NEXT_PUBLIC_API_URL  = https://<backend-domain>
NEXT_PUBLIC_APP_NAME = ScaleX AI
```

> **Order matters:** deploy the backend first, generate its domain, then set the
> frontend's `NEXT_PUBLIC_API_URL` to it and deploy the frontend. Finally set the
> backend's `CORS_ORIGINS` to the frontend domain.

---

## Persistent media (important)

Railway containers have an **ephemeral filesystem** — generated images/videos in
`/app/storage_data` are lost on every redeploy. Attach a **Volume** to the backend
service mounted at `/app/storage_data` (the script attempts this automatically), or
move storage to S3/Cloudflare R2 later via `STORAGE_BACKEND`.

## Notes

- First backend build is slow (~5 min): the image installs Chromium for the URL importer.
- The studio login lives in `frontend/src/lib/auth.ts` (single-user MVP gate — swap for real auth before a public launch).
- Secrets (`.env`, `.env.local`) are gitignored and never pushed; use `.env.example` as the template.
