"""Video service — idea → script → frames → render (product-scoped).

Flow (human-in-the-loop):
  1. create_script  — from the SELECTED idea (or generic), writes a Hinglish
     script + storyboard as a DRAFT.
  2. update / reprompt — edit the script or regenerate it with new notes.
  3. generate_frames — one AI storyboard FRAME image per scene (review before render).
  4. render — a realistic Indian model SPEAKS the script in Hinglish across
     multiple angles (Veo), stitched into one ad. HeyGen avatar is the fallback.
"""
from __future__ import annotations

import asyncio
import math
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.generation import GeneratedVideo
from app.models.idea import Idea
from app.prompts import script as script_prompt
from app.prompts import video as video_prompt
from app.schemas.generation import VideoGenerateRequest, VideoUpdate
from app.services import analytics_service, image_service, mocks
from app.services.ai import heygen, llm, media
from app.services.brief import assemble_brief
from app.services.product_service import _load
from app.storage import storage

logger = get_logger(__name__)

VERTICAL_FORMATS = {"reel", "short", "story"}
_SHOT_ANGLES = [
    "Medium shot: the presenter faces the camera and talks to the viewer",
    "Wide lifestyle shot in a realistic setting: the presenter showcases the product while speaking",
    "Closer three-quarter shot, shallow depth of field: the presenter speaks, product clearly visible",
    "Over-the-shoulder shot: the presenter turns toward camera and speaks",
]


def _idea_dict(idea: Idea | None) -> dict | None:
    if not idea:
        return None
    return {"title": idea.title, "angle": idea.angle, "description": idea.description, "hook": idea.hook}


async def _draft_from_result(db, product, req, result, idea_id) -> GeneratedVideo:
    brief = assemble_brief(product, product.brand)
    storyboard = result.get("storyboard", [])
    first_text = storyboard[0].get("on_screen_text") if storyboard else product.name
    thumb = image_service.render_poster(
        "story" if req.format in VERTICAL_FORMATS else "landscape",
        first_text or product.name,
        brief.get("cta") or "Watch now",
        brief.get("brand_colors") or ["#6D5EF8", "#22D3EE"],
        product.name,
    )
    thumb_key = f"products/{product.id}/videos/{product.id[:8]}-{abs(hash(first_text or '')) % 100000}-thumb.png"
    thumb_url = storage.save_bytes(thumb_key, thumb)
    video = GeneratedVideo(
        product_id=product.id,
        idea_id=idea_id,
        duration=req.duration,
        format=req.format,
        script=result.get("script"),
        storyboard=storyboard,
        voiceover=result.get("voiceover"),
        captions=result.get("captions", []),
        transitions=result.get("transitions", []),
        thumbnail_url=thumb_url,
        status="draft",
        progress=0,
        meta={
            "text_mode": llm.mode,
            "thumb_key": thumb_key,
            # Consistency sheet: same presenter + same setting in every frame/shot.
            "character": result.get("character") or settings.veo_presenter,
            "setting": result.get("setting") or "a fitting real-world location, natural light",
        },
    )
    db.add(video)
    await db.flush()
    await db.refresh(video)
    return video


async def create_script(db: AsyncSession, product_id: str, req: VideoGenerateRequest) -> GeneratedVideo:
    """Draft a Hinglish script from the selected idea (or generic)."""
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    reqd = {"duration": req.duration, "format": req.format, "instructions": req.instructions}

    idea = await db.get(Idea, req.idea_id) if req.idea_id else None
    if idea:
        result = await llm.generate_structured(
            system=script_prompt.SYSTEM,
            prompt=script_prompt.build_prompt(brief, _idea_dict(idea), reqd),
            schema=script_prompt.SCHEMA,
            mock=lambda: mocks.mock_script(brief, _idea_dict(idea) or {}, reqd),
        )
    else:
        result = await llm.generate_structured(
            system=video_prompt.SYSTEM,
            prompt=video_prompt.build_prompt(brief, reqd),
            schema=video_prompt.SCHEMA,
            mock=lambda: mocks.mock_video(brief, reqd),
        )
    video = await _draft_from_result(db, product, req, result, req.idea_id)
    await analytics_service.record_event(
        db, "video_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"stage": "script", "idea_id": req.idea_id},
    )
    return video


async def update(db: AsyncSession, video_id: str, data: VideoUpdate) -> GeneratedVideo:
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(video, field, value)
    await db.flush()
    await db.refresh(video)
    return video


async def reprompt(db: AsyncSession, video_id: str, instructions: str) -> GeneratedVideo:
    """Regenerate the script for the same idea with extra notes."""
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    product = await _load(db, video.product_id)
    brief = assemble_brief(product, product.brand)
    reqd = {"duration": video.duration, "format": video.format, "instructions": instructions}
    idea = await db.get(Idea, video.idea_id) if video.idea_id else None
    if idea:
        result = await llm.generate_structured(
            system=script_prompt.SYSTEM,
            prompt=script_prompt.build_prompt(brief, _idea_dict(idea), reqd),
            schema=script_prompt.SCHEMA,
            mock=lambda: mocks.mock_script(brief, _idea_dict(idea) or {}, reqd),
        )
    else:
        result = await llm.generate_structured(
            system=video_prompt.SYSTEM,
            prompt=video_prompt.build_prompt(brief, reqd),
            schema=video_prompt.SCHEMA,
            mock=lambda: mocks.mock_video(brief, reqd),
        )
    video.script = result.get("script")
    video.voiceover = result.get("voiceover")
    video.storyboard = result.get("storyboard", [])
    video.captions = result.get("captions", [])
    video.transitions = result.get("transitions", [])
    video.status = "draft"
    video.frame_urls = []
    video.video_url = None
    meta = dict(video.meta or {})
    meta["character"] = result.get("character") or meta.get("character") or settings.veo_presenter
    meta["setting"] = result.get("setting") or meta.get("setting") or "a fitting real-world location, natural light"
    video.meta = meta
    await db.flush()
    await db.refresh(video)
    return video


async def _product_photo(db: AsyncSession, product) -> bytes | None:
    """The authentic product photo (curated selection first) — the fidelity anchor."""
    pool = image_service.reference_pool(product)
    if pool:
        ref = await image_service.fetch_reference(pool)
        if ref:
            return ref
    for img in await image_service.list_for_product(db, product.id):
        key = (img.meta or {}).get("storage_key")
        if key and storage.exists(key):
            return storage.read_bytes(key)
    return None


async def _model_seed(db: AsyncSession, product) -> bytes | None:
    """A 'model showcasing the EXACT product' composite (Nano Banana) to seed frames/video.

    Anchored to the authentic product photo so the real product is preserved.
    """
    base = await _product_photo(db, product)
    if base is None:
        return None
    if media.images_enabled():
        model = await media.edit_image(
            base,
            f"Photorealistic advertising photograph: {settings.veo_presenter} naturally holding and "
            "showcasing THIS EXACT product in a fitting real-world setting. CRITICAL: keep the "
            "product identical to the reference — same shape, colours, material, label, logo and "
            "text; do not redesign, restyle or replace it. Natural lighting, realistic skin and "
            "textures, shallow depth of field, the product in sharp focus and clearly visible. "
            "Professional, photorealistic, no text, no watermark.",
        )
        if model:
            return model
    return base


async def generate_frames(db: AsyncSession, product_id: str, video_id: str) -> GeneratedVideo:
    """One AI storyboard FRAME image per scene (reviewable before render).

    Consistency strategy: every frame prompt carries the SAME character + setting
    sheet (from the script), and frames 2..n are edited FROM frame 1 — so the same
    person, outfit and location persist across the whole storyboard. Frames are
    centre-cropped to the video's aspect so nothing downstream letterboxes.
    """
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    seed = await _model_seed(db, product)

    vmeta = dict(video.meta or {})
    character = vmeta.get("character") or settings.veo_presenter
    setting_desc = vmeta.get("setting") or "a fitting real-world location, natural light"
    vertical = video.format in VERTICAL_FORMATS
    aw, ah = (9, 16) if vertical else (16, 9)

    consistency = (
        f"THE PRESENTER (identical in every frame of this storyboard): {character}. "
        f"THE SETTING (same location & light in every frame): {setting_desc}. "
        "Do NOT change the person's face, hair, outfit, or the location between frames."
    )
    realism = (
        "This must look like a real photograph of a real person: natural skin with visible "
        "pores and texture, real hair strands, believable hands, honest eyes — never plastic, "
        "airbrushed, waxy or CGI-like. Photorealistic, motivated natural lighting, shallow "
        "depth of field, tasteful colour grade, editorial commercial quality."
    )

    frame_urls: list[str] = []
    frame_keys: list[str] = []
    anchor: bytes | None = None  # frame 1 → visual anchor for all later frames
    scenes = video.storyboard[:6] or [{"visual": brief.get("usp") or product.name, "on_screen_text": product.name}]
    for i, scene in enumerate(scenes):
        base = anchor if anchor is not None else seed
        continuation = (
            "Continue the SAME shoot as the reference image: same person, same outfit, same "
            "location, same light — only the camera angle and action change to: "
            if anchor is not None
            else "Scene: "
        )
        prompt = (
            f"Cinematic film still (key frame {i + 1}) for a high-end {video.format} ad, "
            f"{aw}:{ah} composition. {consistency} {continuation}{scene.get('visual', '')}. "
            f"The product is clearly visible and EXACTLY as in the reference — same shape, "
            f"colour, material, label, logo and text; never redesign or replace it. {realism} "
            f"No text overlay, no subtitles, no watermark."
        )
        data = None
        if base is not None:
            data = await media.edit_image(base, prompt)
        if data is None and media.images_enabled():
            data = await media.generate_image(prompt, video.format)
        if data is None:
            data = image_service.render_poster(
                "story" if vertical else "landscape", scene.get("on_screen_text") or product.name,
                brief.get("cta") or "", brief.get("brand_colors") or ["#6D5EF8", "#22D3EE"], product.name,
            )
        data = image_service.crop_to_aspect(data, aw, ah)  # full-bleed seeds → no letterboxing
        if anchor is None and data is not None:
            anchor = data
        key = f"products/{product_id}/videos/{video_id[:8]}-frame-{i}.png"
        frame_urls.append(storage.save_bytes(key, data))
        frame_keys.append(key)

    video.frame_urls = frame_urls
    meta = dict(video.meta or {})
    meta["frame_keys"] = frame_keys
    video.meta = meta
    video.status = "frames_ready"
    await db.flush()
    await analytics_service.record_event(
        db, "frames_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"frames": len(frame_urls)},
    )
    await db.refresh(video)
    return video


def _split_script(text: str, n: int) -> list[str]:
    sents = [s.strip() for s in re.split(r"(?<=[.!?\n])\s+", (text or "").strip()) if s.strip()]
    if not sents:
        return [(text or "Check this out.").strip()]
    n = max(1, min(n, len(sents)))
    size = math.ceil(len(sents) / n)
    return [" ".join(sents[i : i + size]) for i in range(0, len(sents), size)][:n]


def _veo_shot_prompt(brief, product, video, line: str, angle: str, has_seed: bool) -> str:
    name = brief.get("product_name") or product.name
    vmeta = video.meta or {}
    character = vmeta.get("character") or settings.veo_presenter
    setting_desc = vmeta.get("setting") or "a fitting real-world location, natural light"
    anim = (
        "Animate the provided reference into a live, moving shot; keep the presenter and product "
        "identical to the reference. " if has_seed else ""
    )
    colors = ", ".join((brief.get("brand_colors") or [])[:2])
    return (
        f"Photorealistic, cinematic {video.format} product commercial for {name}. {anim}{angle}. "
        f"CONSISTENCY (critical — this is one shot of a multi-shot ad): the presenter is "
        f"{character} — the SAME person with the SAME face, hair and outfit in every shot of this "
        f"ad. The location is {setting_desc} — the SAME place and light in every shot. Never swap "
        f"the person, outfit or location. "
        f"Shot on a professional cinema camera: lifelike human with natural skin texture and pores, "
        f"realistic fabric and material detail, true-to-life lighting with soft natural shadows, "
        f"35mm lens, shallow depth of field, gentle organic camera movement (subtle handheld/dolly), "
        f"24fps film look with subtle motion blur — a real filmed advertisement, never CGI or "
        f"AI-looking. "
        f"PRODUCT FIDELITY — the featured product MUST be exactly the product in the reference "
        f"image: identical shape, colour, material, label, logo and text. Never redesign, restyle, "
        f"recolour or substitute it; keep it in sharp focus and clearly visible. "
        f"The presenter speaks directly to camera with accurate, well-timed lip-sync in "
        f"{settings.veo_language}, saying exactly: \"{line[:220]}\". Crystal-clear spoken audio, "
        f"no background-narration clutter. Absolutely no on-screen text, subtitles, captions or "
        f"watermark."
        + (f" Subtle brand-colour accents in the setting: {colors}." if colors else "")
    )


async def begin_render(db: AsyncSession, product_id: str, video_id: str) -> GeneratedVideo:
    """Flip the video to 'rendering' and return at once — the minutes-long Veo work
    then runs in the background (see render_background). Rendering synchronously over
    HTTP times out behind Railway's proxy ('failed to fetch')."""
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    video.status = "rendering"
    video.progress = 5
    video.video_url = None
    await db.flush()
    await db.refresh(video)
    return video


async def render_background(product_id: str, video_id: str) -> None:
    """Run the render off the request path in its own DB session; never leave it stuck."""
    from app.database.session import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as db:
            await _render_impl(db, product_id, video_id)
            await db.commit()
    except Exception as exc:
        logger.exception("render failed for video %s", video_id)
        try:
            async with AsyncSessionLocal() as db:
                v = await db.get(GeneratedVideo, video_id)
                if v:
                    v.status = "error"
                    v.progress = 100
                    v.meta = {**(v.meta or {}), "render_error": str(exc)[:300]}
                    await db.commit()
        except Exception:
            logger.exception("could not mark render error for %s", video_id)


async def _render_impl(db: AsyncSession, product_id: str, video_id: str) -> GeneratedVideo:
    """Render the approved script into a realistic multi-shot Veo ad (Indian, Hinglish)."""
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    script_text = (video.voiceover or video.script or "").strip()
    vertical = video.format in VERTICAL_FORMATS

    # Per-shot seed: use generated frames if present, else one model image.
    frame_keys = (video.meta or {}).get("frame_keys") or []
    frame_seeds = [storage.read_bytes(k) for k in frame_keys if storage.exists(k)]
    model_seed = await _model_seed(db, product) if not frame_seeds else None
    product_ref = await _product_photo(db, product)  # exact product → Veo asset reference

    mp4 = None
    provider = "storyboard"
    order = ["veo", "heygen"] if settings.video_engine == "veo" else ["heygen", "veo"]
    for engine in order:
        if mp4:
            break
        if engine == "veo" and media.video_enabled():
            mp4, provider = await _render_veo(
                brief, product, video, script_text, frame_seeds, model_seed, product_ref
            )
        elif engine == "heygen" and heygen.enabled():
            clip = await heygen.generate_avatar_video(script_text, vertical, f"{product.name} — {video.format}")
            if clip:
                mp4, provider = clip, "heygen"

    meta = dict(video.meta or {})
    if mp4:
        vkey = f"products/{product_id}/videos/{video_id[:8]}.mp4"
        video.video_url = storage.save_bytes(vkey, mp4)
        meta.update({"video_provider": provider, "has_audio": True, "video_key": vkey})
        # Poster = a real frame from the rendered video (not the placeholder poster).
        frame = await media.extract_thumbnail(mp4, at_seconds=1.0)
        if frame:
            tkey = f"products/{product_id}/videos/{video_id[:8]}-vthumb.jpg"
            video.thumbnail_url = storage.save_bytes(tkey, frame)
            meta["thumb_key"] = tkey
    else:
        meta.update({
            "video_provider": "storyboard",
            "has_audio": False,
            "render_note": "Add GOOGLE_API_KEY (Veo) or HEYGEN_API_KEY to render the video.",
        })
    video.meta = meta
    video.status = "ready"
    video.progress = 100
    await db.flush()
    await analytics_service.record_event(
        db, "video_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"stage": "render", "provider": meta.get("video_provider")},
    )
    await db.refresh(video)
    return video


async def _render_veo(brief, product, video, script_text, frame_seeds, model_seed, product_ref=None):
    n = max(1, settings.veo_shots)
    segments = _split_script(script_text, n)
    # product_ref = the authentic product photo → passed to Veo as an ASSET reference so
    # the EXACT product appears in every shot (not just the composite seed frame).
    tasks = []
    for i, seg in enumerate(segments):
        seed = frame_seeds[i] if i < len(frame_seeds) else (frame_seeds[-1] if frame_seeds else model_seed)
        prompt = _veo_shot_prompt(brief, product, video, seg, _SHOT_ANGLES[i % len(_SHOT_ANGLES)], seed is not None)
        tasks.append(
            media.generate_video(prompt, video.format, image_bytes=seed, product_bytes=product_ref)
        )
    results = await asyncio.gather(*tasks)
    clips = [c for c in results if c]
    if not clips:
        return None, "storyboard"
    # Target frame: full-bleed vertical for reels/stories, else landscape.
    w, h = (720, 1280) if video.format in VERTICAL_FORMATS else (1280, 720)
    if len(clips) >= 2 and media.ffmpeg_available():
        stitched = await media.concat_videos(clips, w, h)
        if stitched:
            return stitched, "veo-multishot"
    # Single clip: still crop-to-fill so there are never black bars.
    if media.ffmpeg_available():
        norm = await media.normalize_video(clips[0], w, h)
        if norm:
            return norm, "veo"
    return clips[0], "veo"


async def list_for_product(db: AsyncSession, product_id: str) -> list[GeneratedVideo]:
    rows = await db.execute(
        select(GeneratedVideo)
        .where(GeneratedVideo.product_id == product_id)
        .order_by(GeneratedVideo.created_at.desc())
    )
    return list(rows.scalars().all())


async def set_saved(db: AsyncSession, video_id: str, saved: bool) -> GeneratedVideo | None:
    obj = await db.get(GeneratedVideo, video_id)
    if obj:
        obj.is_saved = saved
        await db.flush()
    return obj


async def delete(db: AsyncSession, video_id: str) -> None:
    obj = await db.get(GeneratedVideo, video_id)
    if obj:
        await db.delete(obj)
        await db.flush()
