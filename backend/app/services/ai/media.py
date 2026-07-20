"""Media generation via Google GenAI — Imagen (images) and Veo (video + audio).

Both are optional: without ``GOOGLE_API_KEY`` (or if a call fails) these return
``None`` and callers fall back to the local renderer / storyboard-only video.

Veo 3 produces video with **native audio** — describing narration and music in
the prompt yields a voiceover track plus background music in the MP4, so no
separate TTS/music step is needed.

The Google SDK is synchronous; calls are off-loaded to a worker thread so they
don't block the event loop.
"""
from __future__ import annotations

import asyncio
import time
from typing import Any

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# image format -> Imagen aspect ratio
IMAGE_ASPECT = {
    "square": "1:1",
    "portrait": "3:4",
    "landscape": "16:9",
    "story": "9:16",
    "carousel": "1:1",
    "poster": "3:4",
    "lifestyle": "4:3",
}
# video duration/format -> Veo aspect ratio
VIDEO_ASPECT_VERTICAL = {"reel", "short", "story", "15s", "30s"}


def images_enabled() -> bool:
    return settings.google_ai_enabled


def video_enabled() -> bool:
    return settings.google_ai_enabled


def _client():
    from google import genai  # lazy import

    return genai.Client(api_key=settings.google_api_key)


# --------------------------------------------------------------------------- #
# Images (Imagen)
# --------------------------------------------------------------------------- #
def _extract_inline_image(resp) -> bytes | None:
    for cand in getattr(resp, "candidates", None) or []:
        content = getattr(cand, "content", None)
        for part in getattr(content, "parts", None) or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return bytes(inline.data)
    return None


# Last image-generation failure reason (surfaced into image meta for debugging).
_last_image_error: str | None = None


def last_image_error() -> str | None:
    return _last_image_error


def _image_configs():
    """Config variants to try — the image model may or may not want response_modalities."""
    from google.genai import types

    variants = []
    for mods in (["IMAGE"], ["TEXT", "IMAGE"]):
        try:
            variants.append(types.GenerateContentConfig(response_modalities=mods))
        except Exception:
            pass
    variants.append(None)  # last resort: no config (older behavior)
    return variants


def _sync_generate_image(prompt: str, aspect: str) -> bytes | None:
    """Text-to-image via Nano Banana (Gemini 2.5 Flash Image)."""
    global _last_image_error
    client = _client()
    full = f"{prompt} Aspect ratio {aspect}, professional advertising photograph."
    for cfg in _image_configs():
        try:
            kwargs: dict[str, Any] = {"model": settings.nano_banana_model, "contents": [full]}
            if cfg is not None:
                kwargs["config"] = cfg
            resp = client.models.generate_content(**kwargs)
            img = _extract_inline_image(resp)
            if img:
                _last_image_error = None
                return img
            _last_image_error = "model returned no inline image"
        except Exception as exc:
            _last_image_error = f"{type(exc).__name__}: {str(exc)[:200]}"
    logger.warning("Nano Banana text-to-image failed (%s)", _last_image_error)
    return None


async def generate_image(prompt: str, image_format: str) -> bytes | None:
    if not images_enabled():
        return None
    aspect = IMAGE_ASPECT.get(image_format, "1:1")
    return await asyncio.to_thread(_sync_generate_image, prompt, aspect)


# --- Nano Banana (Gemini 2.5 Flash Image): edit a real product photo ---------
def _sniff_mime(data: bytes) -> str:
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if data[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def _sync_edit_image(ref: bytes, prompt: str) -> bytes | None:
    global _last_image_error
    from google.genai import types

    client = _client()
    part = types.Part.from_bytes(data=ref, mime_type=_sniff_mime(ref))
    for cfg in _image_configs():
        try:
            kwargs: dict[str, Any] = {"model": settings.nano_banana_model, "contents": [prompt, part]}
            if cfg is not None:
                kwargs["config"] = cfg
            resp = client.models.generate_content(**kwargs)
            img = _extract_inline_image(resp)
            if img:
                _last_image_error = None
                return img
            _last_image_error = "model returned no inline image"
        except Exception as exc:
            _last_image_error = f"{type(exc).__name__}: {str(exc)[:200]}"
    logger.warning("Nano Banana edit failed (%s)", _last_image_error)
    return None


async def edit_image(reference: bytes, prompt: str) -> bytes | None:
    """Restyle a real product photo into a professional shot, keeping the product."""
    if not images_enabled():
        return None
    return await asyncio.to_thread(_sync_edit_image, reference, prompt)


# --------------------------------------------------------------------------- #
# Video (Veo — includes voiceover + music in the generated audio track)
# --------------------------------------------------------------------------- #
def _extract_video_bytes(client, generated_video) -> bytes | None:
    video = getattr(generated_video, "video", None)
    if video is None:
        return None
    # Preferred: SDK downloads bytes onto the Video object.
    try:
        client.files.download(file=video)
    except Exception:
        pass
    data = getattr(video, "video_bytes", None)
    if data:
        return bytes(data)
    # Fallback: save to a temp file then read.
    try:
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            video.save(tmp.name)
            tmp.flush()
            with open(tmp.name, "rb") as fh:
                return fh.read()
    except Exception as exc:
        logger.warning("Veo download failed (%s)", exc)
        return None


# Steer Veo away from the artifacts that break realism / product fidelity.
_NEGATIVE_PROMPT = (
    "cartoon, illustration, anime, 3d render, cgi, video-game look, plastic or waxy skin, "
    "uncanny face, deformed hands, extra fingers, extra limbs, distorted or warped product, "
    "altered logo, changed packaging, wrong label, morphing product, text artifacts, "
    "on-screen text, subtitles, captions, watermark, logo overlay, blurry, low quality, "
    "oversaturated, jittery motion"
)


def _poll_operation(client, operation) -> bytes | None:
    deadline = time.monotonic() + settings.veo_timeout_seconds
    while not getattr(operation, "done", False):
        if time.monotonic() > deadline:
            logger.warning("Veo timed out after %ss", settings.veo_timeout_seconds)
            return None
        time.sleep(8)
        operation = client.operations.get(operation)
    response = getattr(operation, "response", None)
    vids = getattr(response, "generated_videos", None) or []
    if not vids:
        return None
    return _extract_video_bytes(client, vids[0])


def _sync_generate_video(
    prompt: str,
    aspect: str,
    image_bytes: bytes | None = None,
    product_bytes: bytes | None = None,
    negative_prompt: str | None = None,
) -> bytes | None:
    """Generate one realistic clip.

    Fidelity strategy, most-faithful first (each falls back on a *submission* error
    only, so we never pay for more than one real generation):
      1. reference-to-video — the REAL product photo as an ASSET reference so the exact
         product appears, with full realism config;
      2. image-to-video — seed with the model+product composite frame;
      3. text-to-video — prompt only.
    Config also degrades (full realism → safe → minimal) if the preview model rejects a param.
    """
    from google.genai import types

    client = _client()
    neg = negative_prompt or _NEGATIVE_PROMPT

    def make_cfg(level: int, ref=None):
        kw: dict[str, Any] = {"aspect_ratio": aspect}
        if level >= 1:  # safe realism params (widely supported)
            kw.update(negative_prompt=neg, person_generation="allow_adult", generate_audio=True)
        if level >= 2:  # richer params (may be preview-only)
            kw["enhance_prompt"] = True
            # Veo serves 9:16 at 720p; 1080p is landscape-only and would degrade a
            # vertical request to 16:9 (→ letterboxing). Cap vertical to 720p.
            res = settings.veo_resolution
            if aspect == "9:16" and res and res != "720p":
                res = "720p"
            if res:
                kw["resolution"] = res
        if ref:
            kw["reference_images"] = ref
        # Drop any params this SDK version doesn't support (keeps older builds working).
        valid = set(getattr(types.GenerateVideosConfig, "model_fields", None) or {})
        if valid:
            kw = {k: v for k, v in kw.items() if k in valid}
        return types.GenerateVideosConfig(**kw)

    def as_image(b: bytes):
        return types.Image(image_bytes=b, mime_type=_sniff_mime(b))

    # Reference-to-video (exact-product asset) is only on newer google-genai builds.
    # Guard it so an older SDK degrades to image-to-video instead of crashing the render.
    ref_list = None
    if (
        product_bytes
        and hasattr(types, "VideoGenerationReferenceImage")
        and hasattr(types, "VideoGenerationReferenceType")
    ):
        try:
            ref_list = [
                types.VideoGenerationReferenceImage(
                    image=as_image(product_bytes),
                    reference_type=types.VideoGenerationReferenceType.ASSET,
                )
            ]
        except Exception as exc:
            logger.warning("Veo reference-images unavailable (%s) — using image-to-video", exc)
            ref_list = None

    # (extra generate_videos kwargs, config) — tried until one SUBMITS.
    attempts: list[tuple[dict, Any]] = []
    if ref_list:
        attempts.append(({}, make_cfg(2, ref_list)))
        attempts.append(({}, make_cfg(1, ref_list)))
    if image_bytes:
        img = as_image(image_bytes)
        attempts.append(({"image": img}, make_cfg(2)))
        attempts.append(({"image": img}, make_cfg(1)))
        attempts.append(({"image": img}, make_cfg(0)))
    attempts.append(({}, make_cfg(2)))
    attempts.append(({}, make_cfg(0)))

    operation = None
    for i, (extra, cfg) in enumerate(attempts):
        try:
            operation = client.models.generate_videos(
                model=settings.veo_model, prompt=prompt, config=cfg, **extra
            )
            break
        except Exception as exc:  # invalid param/mode for this model → try the next
            logger.warning("Veo submit attempt %d failed (%s)", i, str(exc)[:200])
            operation = None
            continue

    if operation is None:
        return None
    try:
        return _poll_operation(client, operation)
    except Exception as exc:
        logger.warning("Veo poll failed (%s)", exc)
        return None


def build_veo_prompt(brief: dict[str, Any], storyboard: list[dict[str, Any]], req: dict[str, Any]) -> str:
    """Compose a Veo prompt that asks for a voiceover track + background music."""
    name = brief.get("product_name") or "the product"
    scenes = "; ".join(
        f"{s.get('scene', '')}: {s.get('visual', '')}".strip(": ")
        for s in storyboard[:6]
    )
    vo = " ".join(s.get("voiceover", "") for s in storyboard[:6]).strip()
    return (
        f"A polished {req.get('format', 'reel')} advertisement for {name}. "
        f"Scenes: {scenes}. "
        f"Include a confident voiceover narration saying: \"{vo or brief.get('usp', '')}\". "
        f"Add upbeat, modern background music that matches the energy. "
        f"Cinematic lighting, brand colors {', '.join(brief.get('brand_colors', [])[:2])}, "
        f"crisp product shots, smooth transitions."
    )


async def generate_video(
    prompt: str,
    duration_or_format: str,
    image_bytes: bytes | None = None,
    product_bytes: bytes | None = None,
    negative_prompt: str | None = None,
) -> bytes | None:
    """image_bytes = first-frame composite seed; product_bytes = the REAL product photo
    passed as an ASSET reference so the exact product is preserved in the clip."""
    if not video_enabled():
        return None
    aspect = "9:16" if duration_or_format in VIDEO_ASPECT_VERTICAL else "16:9"
    return await asyncio.to_thread(
        _sync_generate_video, prompt, aspect, image_bytes, product_bytes, negative_prompt
    )


# --------------------------------------------------------------------------- #
# Stitch multiple clips into one multi-angle ad (requires ffmpeg)
# --------------------------------------------------------------------------- #
def ffmpeg_available() -> bool:
    import shutil

    return shutil.which("ffmpeg") is not None


def _sync_concat(clips: list[bytes], w: int = 720, h: int = 1280) -> bytes | None:
    import os
    import subprocess
    import tempfile

    if len(clips) < 2 or not ffmpeg_available():
        return None
    tmp = tempfile.mkdtemp(prefix="scalex_concat_")
    try:
        paths = []
        for i, data in enumerate(clips):
            p = os.path.join(tmp, f"c{i}.mp4")
            with open(p, "wb") as fh:
                fh.write(data)
            paths.append(p)
        out = os.path.join(tmp, "out.mp4")
        # Re-encode + concat filter so slightly-different streams still join. Each clip is
        # scaled to COVER the target frame then centre-cropped (crop-to-fill) so the output
        # is full-bleed with NO black bars, whatever aspect the source clip came back as.
        n = len(paths)
        inputs: list[str] = []
        for p in paths:
            inputs += ["-i", p]
        parts = "".join(
            f"[{i}:v]scale={w}:{h}:force_original_aspect_ratio=increase,"
            f"crop={w}:{h},setsar=1,fps=24[v{i}];"
            f"[{i}:a]aresample=44100[a{i}];"
            for i in range(n)
        )
        concat_in = "".join(f"[v{i}][a{i}]" for i in range(n))
        filt = f"{parts}{concat_in}concat=n={n}:v=1:a=1[v][a]"
        cmd = ["ffmpeg", "-y", *inputs, "-filter_complex", filt,
               "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-c:a", "aac",
               "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, timeout=180)
        if r.returncode != 0:
            logger.warning("ffmpeg concat failed: %s", r.stderr.decode()[-400:])
            return None
        with open(out, "rb") as fh:
            return fh.read()
    except Exception as exc:
        logger.warning("concat error (%s)", exc)
        return None
    finally:
        import shutil as _sh

        _sh.rmtree(tmp, ignore_errors=True)


async def concat_videos(clips: list[bytes], w: int = 720, h: int = 1280) -> bytes | None:
    return await asyncio.to_thread(_sync_concat, clips, w, h)


def _sync_normalize(clip: bytes, w: int, h: int) -> bytes | None:
    """Crop-to-fill a single clip to exactly w×h (removes any letterboxing)."""
    import os
    import subprocess
    import tempfile

    if not clip or not ffmpeg_available():
        return None
    tmp = tempfile.mkdtemp(prefix="scalex_norm_")
    try:
        src = os.path.join(tmp, "in.mp4")
        out = os.path.join(tmp, "out.mp4")
        with open(src, "wb") as fh:
            fh.write(clip)
        vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1"
        cmd = ["ffmpeg", "-y", "-i", src, "-vf", vf, "-c:v", "libx264",
               "-c:a", "aac", "-movflags", "+faststart", out]
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode != 0 or not os.path.exists(out):
            logger.warning("ffmpeg normalize failed: %s", r.stderr.decode()[-300:])
            return None
        with open(out, "rb") as fh:
            return fh.read()
    except Exception as exc:
        logger.warning("normalize error (%s)", exc)
        return None
    finally:
        import shutil as _sh

        _sh.rmtree(tmp, ignore_errors=True)


async def normalize_video(clip: bytes, w: int = 720, h: int = 1280) -> bytes | None:
    return await asyncio.to_thread(_sync_normalize, clip, w, h)


# --------------------------------------------------------------------------- #
# Extract a real still frame from the rendered video (for the thumbnail)
# --------------------------------------------------------------------------- #
def _sync_extract_frame(mp4: bytes, at_seconds: float = 1.0) -> bytes | None:
    import os
    import subprocess
    import tempfile

    if not mp4 or not ffmpeg_available():
        return None
    tmp = tempfile.mkdtemp(prefix="scalex_thumb_")
    try:
        src = os.path.join(tmp, "in.mp4")
        out = os.path.join(tmp, "thumb.jpg")
        with open(src, "wb") as fh:
            fh.write(mp4)
        # Grab one representative frame a beat into the clip.
        cmd = ["ffmpeg", "-y", "-ss", str(at_seconds), "-i", src,
               "-frames:v", "1", "-q:v", "3", out]
        r = subprocess.run(cmd, capture_output=True, timeout=60)
        if r.returncode != 0 or not os.path.exists(out):
            # Retry at t=0 for very short clips.
            cmd[3] = "0"
            r = subprocess.run(cmd, capture_output=True, timeout=60)
            if r.returncode != 0 or not os.path.exists(out):
                logger.warning("thumbnail extract failed: %s", r.stderr.decode()[-300:])
                return None
        with open(out, "rb") as fh:
            return fh.read()
    except Exception as exc:
        logger.warning("thumbnail extract error (%s)", exc)
        return None
    finally:
        import shutil as _sh

        _sh.rmtree(tmp, ignore_errors=True)


async def extract_thumbnail(mp4: bytes, at_seconds: float = 1.0) -> bytes | None:
    """Pull a real still frame from a rendered MP4 to use as its poster."""
    return await asyncio.to_thread(_sync_extract_frame, mp4, at_seconds)
