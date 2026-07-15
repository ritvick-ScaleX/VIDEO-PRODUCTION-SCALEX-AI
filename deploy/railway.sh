#!/usr/bin/env bash
# =============================================================================
# ScaleX AI — one-shot Railway deploy
# -----------------------------------------------------------------------------
# Provisions a full Railway project from this repo:
#   • Postgres + Redis
#   • backend service   (FastAPI, ./backend/Dockerfile)  + persistent volume
#   • frontend service  (Next.js, ./frontend/Dockerfile)
#   • all environment variables wired between services
#   • public domains for both, with CORS + API URL cross-linked
#
# PREREQUISITES (one time):
#   1. Install the CLI:   npm i -g @railway/cli   (or: brew install railway)
#   2. Log in:            railway login
#   3. Run this script from the repo root:   bash deploy/railway.sh
#
# AI keys: read from backend/.env if present, otherwise you'll be prompted.
# Re-running is safe-ish, but it's designed for a fresh project. Targets Railway
# CLI v4. If a command's flags differ on your version, the step is printed so you
# can finish it in the dashboard.
# =============================================================================
set -euo pipefail

PROJECT_NAME="${PROJECT_NAME:-scalex-ai}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

say()  { printf "\n\033[1;35m▸ %s\033[0m\n" "$*"; }
ok()   { printf "  \033[1;32m✓\033[0m %s\n" "$*"; }
warn() { printf "  \033[1;33m!\033[0m %s\n" "$*"; }
die()  { printf "\n\033[1;31m✗ %s\033[0m\n" "$*"; exit 1; }

# --- preflight ---------------------------------------------------------------
command -v railway >/dev/null 2>&1 || die "Railway CLI not found. Install: npm i -g @railway/cli"
railway whoami >/dev/null 2>&1 || die "Not logged in. Run: railway login"
ok "Railway CLI ready ($(railway whoami 2>/dev/null | tail -1))"

# --- AI keys (from backend/.env or prompt) -----------------------------------
OPENAI_API_KEY="${OPENAI_API_KEY:-}"; GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"
OPENAI_MODEL="${OPENAI_MODEL:-gpt-4o}"; VEO_MODEL="${VEO_MODEL:-veo-3.1-fast-generate-preview}"
if [ -f backend/.env ]; then
  set -a; . backend/.env 2>/dev/null || true; set +a
fi
[ -z "${OPENAI_API_KEY}" ] && read -rp "OpenAI API key (blank = mock text): " OPENAI_API_KEY
[ -z "${GOOGLE_API_KEY}" ] && read -rp "Google API key (blank = mock images/video): " GOOGLE_API_KEY

# --- project + databases -----------------------------------------------------
say "Creating project '$PROJECT_NAME' + Postgres + Redis"
railway init -n "$PROJECT_NAME"
railway add --database postgres
railway add --database redis
ok "Databases provisioned"

# --- backend service ---------------------------------------------------------
say "Creating backend service"
railway add --service backend
# Wire env. DATABASE_URL is normalised to asyncpg by the app; RAILWAY_PRIVATE_DOMAIN keeps DB traffic internal.
railway variables --service backend \
  --set 'DATABASE_URL=${{Postgres.DATABASE_URL}}' \
  --set 'REDIS_URL=${{Redis.REDIS_URL}}' \
  --set 'RUN_MIGRATIONS_ON_START=true' \
  --set 'ENVIRONMENT=production' \
  --set 'VIDEO_ENGINE=veo' \
  --set 'STORAGE_BACKEND=local' \
  --set 'STORAGE_DIR=/app/storage_data' \
  --set "OPENAI_API_KEY=${OPENAI_API_KEY}" \
  --set "OPENAI_MODEL=${OPENAI_MODEL}" \
  --set "GOOGLE_API_KEY=${GOOGLE_API_KEY}" \
  --set "VEO_MODEL=${VEO_MODEL}" \
  --set 'CORS_ORIGINS=*'
ok "Backend variables set"

# Persistent disk for generated images/videos (survives redeploys).
railway volume add --service backend --mount-path /app/storage_data 2>/dev/null \
  && ok "Volume mounted at /app/storage_data" \
  || warn "Could not auto-create volume — add one in the dashboard (mount: /app/storage_data)"

say "Deploying backend (Docker build — first build pulls Chromium, ~5 min)"
( cd backend && railway up --service backend --ci )
railway domain --service backend || true
BACKEND_URL="$(railway domain --service backend 2>/dev/null | grep -oE 'https?://[a-zA-Z0-9._-]+' | head -1)"
[ -z "$BACKEND_URL" ] && BACKEND_URL="$(railway variables --service backend --kv 2>/dev/null | grep -iE 'RAILWAY_PUBLIC_DOMAIN' | head -1 | sed -E 's/.*=//' | sed 's#^#https://#')"
[ -z "$BACKEND_URL" ] && warn "Couldn't auto-detect backend URL — grab it from the dashboard." || ok "Backend live at $BACKEND_URL"

# Point static asset URLs at the backend's public domain.
if [ -n "$BACKEND_URL" ]; then
  railway variables --service backend --set "STORAGE_PUBLIC_URL=${BACKEND_URL}/static" >/dev/null && ok "STORAGE_PUBLIC_URL set"
fi

# --- frontend service --------------------------------------------------------
say "Creating frontend service"
railway add --service frontend
# NEXT_PUBLIC_* are baked at BUILD time → must be set before `railway up`.
railway variables --service frontend \
  --set "NEXT_PUBLIC_API_URL=${BACKEND_URL:-CHANGE_ME}" \
  --set 'NEXT_PUBLIC_APP_NAME=ScaleX AI' >/dev/null
ok "Frontend variables set"

say "Deploying frontend"
( cd frontend && railway up --service frontend --ci )
railway domain --service frontend || true
FRONTEND_URL="$(railway domain --service frontend 2>/dev/null | grep -oE 'https?://[a-zA-Z0-9._-]+' | head -1)"
[ -n "$FRONTEND_URL" ] && ok "Frontend live at $FRONTEND_URL" || warn "Grab the frontend URL from the dashboard."

# --- lock CORS to the frontend origin ---------------------------------------
if [ -n "${FRONTEND_URL:-}" ]; then
  say "Locking backend CORS to $FRONTEND_URL"
  railway variables --service backend --set "CORS_ORIGINS=${FRONTEND_URL}" >/dev/null && ok "CORS set (backend will redeploy)"
fi

say "Done 🎉"
cat <<EOF
  Frontend : ${FRONTEND_URL:-<set in dashboard>}
  Backend  : ${BACKEND_URL:-<set in dashboard>}

  If a URL shows blank above, open the Railway dashboard → the service → Settings →
  Networking → "Generate Domain", then set the matching variable:
    • frontend  NEXT_PUBLIC_API_URL = https://<backend-domain>   (then redeploy frontend)
    • backend   CORS_ORIGINS        = https://<frontend-domain>
    • backend   STORAGE_PUBLIC_URL  = https://<backend-domain>/static

  Login to the studio with the credentials in frontend/src/lib/auth.ts.
EOF
