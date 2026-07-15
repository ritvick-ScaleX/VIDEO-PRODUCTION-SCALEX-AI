"""HeyGen talking-head avatar video.

Given an approved script, HeyGen renders a presenter avatar speaking it (its own
neural voice), which we download as an MP4. Optional: without ``HEYGEN_API_KEY``
(or on any failure) this returns ``None`` and the caller falls back to the
storyboard-only draft.

The API is synchronous + polled, so calls run in a worker thread.
"""
from __future__ import annotations

import asyncio
import random
import time
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_BASE = "https://api.heygen.com"
_cache: dict[str, Any] = {}

# Best-effort Indian-presenter detection (HeyGen doesn't expose ethnicity, so we
# match common Indian names in the avatar label).
_INDIAN_NAME_HINTS = (
    "raj", "priya", "amit", "neha", "arjun", "ananya", "rahul", "anjali",
    "vikram", "kiran", "deepak", "pooja", "sanjay", "meera", "aditi", "ravi",
    "sneha", "rohan", "isha", "karan", "divya", "nikhil", "riya", "aarav",
    "ishaan", "kavya", "dev", "tara", "arya", "veer", "ayaan", "sai", "anushka",
)


def enabled() -> bool:
    return settings.heygen_enabled


def _headers() -> dict[str, str]:
    return {"X-Api-Key": settings.heygen_api_key, "Content-Type": "application/json"}


def _text(obj: dict, *keys: str) -> str:
    return " ".join(str(obj.get(k, "")) for k in keys).lower()


def _fetch_lists(client) -> tuple[list[dict], list[dict]]:
    if "avatars" not in _cache:
        try:
            r = client.get(f"{_BASE}/v2/avatars", headers=_headers(), timeout=30)
            d = r.json().get("data") or {}
            _cache["avatars"] = (d.get("avatars") or []) + (d.get("talking_photos") or [])
        except Exception as exc:
            logger.warning("HeyGen avatar list failed (%s)", exc)
            _cache["avatars"] = []
    if "voices" not in _cache:
        try:
            r = client.get(f"{_BASE}/v2/voices", headers=_headers(), timeout=30)
            _cache["voices"] = (r.json().get("data") or {}).get("voices", [])
        except Exception as exc:
            logger.warning("HeyGen voice list failed (%s)", exc)
            _cache["voices"] = []
    return _cache["avatars"], _cache["voices"]


def _pick(client) -> tuple[str | None, str | None]:
    """Resolve (avatar_id, voice_id): env pins win; else Indian + rotating avatar."""
    region = (settings.heygen_region or "india").lower()
    avatars, voices = _fetch_lists(client)

    # --- Avatar: prefer regional look, rotate for variety ---
    avatar = settings.heygen_avatar_id or None
    if not avatar and avatars:
        regional = [
            a for a in avatars
            if any(h in _text(a, "avatar_name", "name") for h in _INDIAN_NAME_HINTS)
            or region in _text(a, "avatar_name", "name")
        ]
        pool = regional or avatars
        chosen = random.choice(pool) if settings.heygen_rotate_avatars else pool[0]
        avatar = chosen.get("avatar_id") or chosen.get("talking_photo_id")

    # --- Voice: prefer regional accent (e.g. Indian English) ---
    voice = settings.heygen_voice_id or _cache.get("voice")
    if not voice and voices:
        regional = [
            v for v in voices
            if region in _text(v, "name", "language", "locale", "accent")
            or "en-in" in _text(v, "locale", "language")
        ]
        english = [v for v in voices if "english" in _text(v, "language")]
        pool = regional or english or voices
        chosen = random.choice(pool)
        voice = chosen.get("voice_id")
        _cache["voice"] = voice  # keep the accent consistent across renders

    return avatar, voice


def _sync_generate(script: str, vertical: bool, title: str) -> bytes | None:
    try:
        import httpx

        with httpx.Client(follow_redirects=True) as client:
            avatar, voice = _pick(client)
            if not avatar or not voice:
                logger.warning("HeyGen: no avatar/voice available")
                return None
            logger.info("HeyGen render with avatar=%s voice=%s", avatar, voice)

            w, h = (720, 1280) if vertical else (1280, 720)
            payload: dict[str, Any] = {
                "title": title[:80],
                "video_inputs": [
                    {
                        "character": {"type": "avatar", "avatar_id": avatar, "avatar_style": "normal"},
                        "voice": {"type": "text", "input_text": script[:1500], "voice_id": voice},
                        "background": {"type": "color", "value": "#0B0B12"},
                    }
                ],
                "dimension": {"width": w, "height": h},
            }
            r = client.post(f"{_BASE}/v2/video/generate", headers=_headers(), json=payload, timeout=60)
            r.raise_for_status()
            video_id = r.json().get("data", {}).get("video_id")
            if not video_id:
                logger.warning("HeyGen: no video_id in response")
                return None

            deadline = time.monotonic() + settings.heygen_timeout_seconds
            video_url = None
            while time.monotonic() < deadline:
                time.sleep(8)
                s = client.get(
                    f"{_BASE}/v1/video_status.get",
                    headers=_headers(),
                    params={"video_id": video_id},
                    timeout=30,
                )
                d = s.json().get("data", {})
                status = d.get("status")
                if status == "completed":
                    video_url = d.get("video_url")
                    break
                if status in {"failed", "error"}:
                    logger.warning("HeyGen render failed: %s", d.get("error"))
                    return None
            if not video_url:
                logger.warning("HeyGen render timed out")
                return None

            dl = client.get(video_url, timeout=120)
            dl.raise_for_status()
            return dl.content
    except Exception as exc:
        logger.warning("HeyGen generation failed (%s)", exc)
        return None


async def generate_avatar_video(script: str, vertical: bool, title: str) -> bytes | None:
    if not enabled():
        return None
    return await asyncio.to_thread(_sync_generate, script, vertical, title)
