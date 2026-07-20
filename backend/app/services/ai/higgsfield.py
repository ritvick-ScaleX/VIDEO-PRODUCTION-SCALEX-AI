"""Higgsfield video generation — extra models rendered alongside our Veo pipeline.

Higgsfield's Cloud API (https://platform.higgsfield.ai):
  • auth header:  Authorization: Key <KEY_ID>:<KEY_SECRET>
  • submit:       POST /v1/image2video/dop
                  body -> {"params": {"model": <enum>, "prompt": str,
                                       "input_images": [{"type":"image_url","image_url":URL}]}}
                  model enum (this account): 'dop-lite' | 'dop-preview' | 'dop-turbo'
  • result:       a job set whose finished job carries a result video URL (mp4)

NOTE: this account's catalogue exposes only Higgsfield DoP video (+ Soul images) —
NOT Seedance / Kling / Gemini. Those must be enabled on the Higgsfield plan; once
they are, add them to HIGGSFIELD_MODELS (JSON env) — no code change needed.

Image-to-video needs a PUBLIC image URL (our generated storyboard frames are
served from STORAGE_PUBLIC_URL, which is publicly reachable in production).

Everything degrades gracefully: no creds or any failure → returns (None, reason)
so the caller can surface the real reason (e.g. "Not enough credits") in the UI.
Model ids / endpoints are config-driven (settings.higgsfield_models) so the
catalog can change without a code edit.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_DONE = {"completed", "succeeded", "success", "done", "finished"}
_FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


def enabled() -> bool:
    return settings.higgsfield_enabled


def models() -> list[dict[str, Any]]:
    return list(settings.higgsfield_models or [])


def _auth_header() -> str:
    return f"Key {settings.higgsfield_api_key}:{settings.higgsfield_secret}"


def _find_url(obj: Any) -> str | None:
    """Depth-first search for the finished video URL in an arbitrary JSON blob."""
    if isinstance(obj, str):
        return obj if obj.startswith("http") and obj.lower().split("?")[0].endswith(
            (".mp4", ".mov", ".webm")
        ) else None
    if isinstance(obj, dict):
        # Prefer explicit result fields first.
        for k in ("url", "video_url", "output_url", "result_url"):
            v = obj.get(k)
            if isinstance(v, str) and v.startswith("http"):
                return v
        for v in obj.values():
            found = _find_url(v)
            if found:
                return found
    if isinstance(obj, list):
        for v in obj:
            found = _find_url(v)
            if found:
                return found
    return None


def _find_status(obj: Any) -> str | None:
    if isinstance(obj, dict):
        for k in ("status", "state"):
            v = obj.get(k)
            if isinstance(v, str):
                return v.lower()
        for v in obj.values():
            s = _find_status(v)
            if s:
                return s
    if isinstance(obj, list):
        for v in obj:
            s = _find_status(v)
            if s:
                return s
    return None


def _find_id(obj: dict) -> str | None:
    for k in ("id", "job_set_id", "jobSetId", "job_id", "jobId", "set_id"):
        v = obj.get(k)
        if isinstance(v, str):
            return v
    return None


def _error_text(resp) -> str:
    """Turn a Higgsfield error response into a short human-readable reason."""
    try:
        data = resp.json()
    except Exception:
        return (resp.text or "")[:200].strip() or f"HTTP {resp.status_code}"
    if isinstance(data, dict):
        d = data.get("detail")
        if isinstance(d, str):
            return d[:200]
        if isinstance(d, list) and d:
            msgs = [str(e.get("msg") or e) for e in d if isinstance(e, dict)]
            if msgs:
                return "; ".join(msgs)[:200]
    return str(data)[:200]


def _sync_generate(
    model_def: dict[str, Any], prompt: str, image_url: str
) -> tuple[bytes | None, str | None]:
    """Returns (mp4_bytes, None) on success, or (None, reason) on any failure."""
    import httpx

    base = settings.higgsfield_base_url.rstrip("/")
    endpoint = model_def.get("endpoint") or "/v1/image2video/dop"
    # DoP schema: everything nests under "params".
    params: dict[str, Any] = {
        "model": model_def.get("model"),
        "prompt": prompt,
        "input_images": [{"type": "image_url", "image_url": image_url}],
        **(model_def.get("params") or {}),
    }
    body = {"params": params}
    headers = {"Authorization": _auth_header(), "Content-Type": "application/json"}
    deadline = time.monotonic() + settings.higgsfield_timeout_seconds
    label = model_def.get("label", model_def.get("model", "higgsfield"))
    try:
        with httpx.Client(timeout=60) as c:
            r = c.post(f"{base}{endpoint}", json=body, headers=headers)
            if r.status_code >= 400:
                reason = _error_text(r)
                logger.warning("Higgsfield %s submit %s: %s", label, r.status_code, reason)
                return None, f"{label}: {reason}"
            data = r.json()
            # Immediate result?
            url = _find_url(data)
            job_id = _find_id(data) if isinstance(data, dict) else None
            # Poll the job set until it finishes.
            while not url and job_id and time.monotonic() < deadline:
                time.sleep(6)
                for poll in (f"{base}/v1/job-sets/{job_id}", f"{base}/v1/jobs/{job_id}",
                             f"{base}{endpoint}/{job_id}"):
                    try:
                        pr = c.get(poll, headers=headers)
                    except Exception:
                        continue
                    if pr.status_code >= 400:
                        continue
                    pdata = pr.json()
                    st = _find_status(pdata)
                    if st in _FAILED:
                        reason = _error_text(pr)
                        logger.warning("Higgsfield %s failed: %s", label, reason)
                        return None, f"{label}: {reason}"
                    url = _find_url(pdata)
                    if url or st in _DONE:
                        break
            if not url:
                logger.warning("Higgsfield %s: no result url before timeout", label)
                return None, f"{label}: timed out before the video was ready"
            # Download the finished mp4.
            vr = c.get(url, headers=headers, follow_redirects=True, timeout=120)
            if vr.status_code == 200 and vr.content:
                return vr.content, None
            logger.warning("Higgsfield %s download %s", label, vr.status_code)
            return None, f"{label}: could not download the finished video (HTTP {vr.status_code})"
    except Exception as exc:
        logger.warning("Higgsfield %s error: %s", label, exc)
        return None, f"{label}: {exc}"


async def generate_video(
    model_def: dict[str, Any], prompt: str, image_url: str
) -> tuple[bytes | None, str | None]:
    """Render one clip with a Higgsfield model.

    Returns (mp4_bytes, None) on success, or (None, reason) on any failure so the
    caller can show the real reason (missing credits, model not on plan, …).
    """
    if not enabled():
        return None, "Higgsfield is not configured (missing API key/secret)."
    if not image_url:
        return None, "No public frame URL available to seed the video."
    return await asyncio.to_thread(_sync_generate, model_def, prompt, image_url)
