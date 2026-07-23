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
from app.services.ai import heygen, higgsfield, llm, media
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


def _compose_script(result: dict) -> str:
    """The COMPLETE script the presenter delivers.

    The model's own 'script' field is often just the first scene, so rebuild the full
    thing from every storyboard scene: the end-to-end spoken voiceover first, then a
    scene-by-scene breakdown. Falls back to the raw script/voiceover if there's no
    storyboard.
    """
    sb = result.get("storyboard") or []
    spoken = " ".join(
        str(s.get("voiceover") or "").strip() for s in sb if str(s.get("voiceover") or "").strip()
    ).strip() or str(result.get("voiceover") or "").strip()
    if not sb:
        return str(result.get("script") or spoken or "").strip()
    out: list[str] = []
    if spoken:
        out += ["FULL VOICEOVER (spoken end-to-end):", spoken, "", "— SCENE BREAKDOWN —"]
    for i, s in enumerate(sb, 1):
        title = str(s.get("scene") or "").strip()
        out.append(f"SCENE {i}" + (f" — {title}" if title else ""))
        if s.get("visual"):
            out.append(f"  Visual: {str(s['visual']).strip()}")
        if s.get("voiceover"):
            out.append(f'  Says: "{str(s["voiceover"]).strip()}"')
        if s.get("on_screen_text"):
            out.append(f"  On-screen: {str(s['on_screen_text']).strip()}")
        if s.get("duration"):
            out.append(f"  Duration: {str(s['duration']).strip()}")
        out.append("")
    return "\n".join(out).strip()


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
        script=_compose_script(result),
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
            # Consistency sheet: same presenter, same voice, same setting in every frame/shot.
            "character": result.get("character") or settings.veo_presenter,
            "voice": result.get("voice") or settings.veo_voice,
            "setting": result.get("setting") or settings.veo_setting_bias,
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
    video.script = _compose_script(result)
    video.voiceover = result.get("voiceover")
    video.storyboard = result.get("storyboard", [])
    video.captions = result.get("captions", [])
    video.transitions = result.get("transitions", [])
    video.status = "draft"
    video.frame_urls = []
    video.video_url = None
    meta = dict(video.meta or {})
    meta["character"] = result.get("character") or meta.get("character") or settings.veo_presenter
    meta["voice"] = result.get("voice") or meta.get("voice") or settings.veo_voice
    meta["setting"] = result.get("setting") or meta.get("setting") or settings.veo_setting_bias
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


# Locks the product's packaging FORM FACTOR (jar vs tube vs bottle …), not just its
# label/colours — Nano Banana otherwise "normalises" e.g. a sunscreen jar into a tube.
_PACKAGING_FIDELITY = (
    "The product MUST stay IDENTICAL to the reference image, including its exact "
    "packaging/container FORMAT and proportions — if the reference is a jar/tub keep a jar/tub, "
    "if a bottle keep a bottle, if a tube keep a tube, if a pump keep a pump; NEVER convert it to "
    "a different container type (e.g. do not turn a jar into a tube), even if unusual for the "
    "category. Keep the same overall shape, size, colours, material, finish, cap/lid, label, logo "
    "and text. Do not redesign, restyle, resize, recolour or replace it."
)


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
            f"showcasing THIS EXACT product in a fitting real-world setting. {_PACKAGING_FIDELITY} "
            "Natural lighting, realistic skin and textures, shallow depth of field, the product in "
            "sharp focus and clearly visible. Professional, photorealistic, no text, no watermark.",
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
    # The REAL product photo — re-anchored into every frame so Nano Banana can't
    # quietly redraw it into a different container (jar → tube) during scene edits.
    product_ref = await _product_photo(db, product)

    vmeta = dict(video.meta or {})
    character = vmeta.get("character") or settings.veo_presenter
    setting_desc = vmeta.get("setting") or "a fitting real-world location, natural light"
    vertical = video.format in VERTICAL_FORMATS
    aw, ah = (9, 16) if vertical else (16, 9)

    consistency = (
        f"THE PRESENTER (identical in every frame of this storyboard): {character}. "
        f"Her/his face, hair and build must NEVER change between frames. "
        f"PRIMARY SETTING (the default location & light): {setting_desc}. This must look like a "
        "REAL, authentic Indian home / everyday Indian location — lived-in and believable, never "
        "a generic studio or artificial AI-looking backdrop. Keep this setting unless THIS scene's "
        "direction explicitly names a different location — a scripted location change is allowed, "
        "but the presenter stays the identical person."
    )
    realism = (
        "This must look like a real, candid smartphone photo a genuine person snapped at home — "
        "authentic UGC style: natural available indoor light, true-to-life colours, the mild "
        "imperfection of a phone camera, NOT a glossy studio or editorial shoot. Real skin with "
        "visible pores and texture, real hair strands, believable hands and honest eyes — never "
        "plastic, airbrushed, waxy or CGI-like."
    )

    frame_urls: list[str] = []
    frame_keys: list[str] = []
    anchor: bytes | None = None  # frame 1 → visual anchor for all later frames
    scenes = video.storyboard[:max(1, settings.veo_shots)] or [{"visual": brief.get("usp") or product.name, "on_screen_text": product.name}]
    for i, scene in enumerate(scenes):
        base = anchor if anchor is not None else seed
        continuation = (
            "Continue the SAME shoot as the reference image — the SAME person with the identical "
            "face, hair and build. Keep the same outfit and location unless this scene's "
            "direction explicitly changes them. New scene direction: "
            if anchor is not None
            else "Scene: "
        )
        prompt = (
            f"Candid, authentic UGC-style smartphone photo (key frame {i + 1}) for a "
            f"real-feeling {video.format} ad, {aw}:{ah} composition. {consistency} "
            f"{continuation}{scene.get('visual', '')}. "
            f"The product is clearly visible and EXACTLY as in the reference image. "
            f"{_PACKAGING_FIDELITY} {realism} "
            f"No text overlay, no subtitles, no watermark."
        )
        data = None
        is_ai = False
        if base is not None:
            data = await media.edit_image(base, prompt)
            if data:
                is_ai = True
        if data is None and media.images_enabled():
            data = await media.generate_image(prompt, video.format)
            if data:
                is_ai = True
        if data is None:
            data = image_service.render_poster(
                "story" if vertical else "landscape", scene.get("on_screen_text") or product.name,
                brief.get("cta") or "", brief.get("brand_colors") or ["#6D5EF8", "#22D3EE"], product.name,
            )
        # Re-anchor the EXACT product from the real photo (the model tends to redraw
        # it into a generic container during large scene edits).
        if is_ai and product_ref and media.images_enabled():
            fixed = await media.compose_images(
                [data, product_ref],
                "Keep the person, pose, hands, framing and background of the FIRST image exactly as "
                "they are. The product the person is holding or showing MUST be the EXACT product "
                "in the SECOND image — copy its real container FORMAT (jar/tub/bottle/tube/pump), "
                "overall shape and proportions, lid/cap, label layout, logo, colours and every bit "
                "of text pixel-faithfully; only adapt its scale, angle and lighting so it sits "
                "naturally in the scene. Do NOT invent or substitute a different product, and do "
                "not change anything else in the image.",
            )
            if fixed:
                data = fixed
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


# Full-depth, paragraph-form Veo 3.1 shot brief (UGC meta-ad). Designed as a real
# creative-team shot note: model, background, the exact spoken meta-ad line, product
# fidelity to the attached reference image, and frame-accurate lip-sync. Filled via
# str.format() — every {placeholder} below is supplied in _veo_shot_prompt().
_VEO_PROMPT_TEMPLATE = (
    "This is one shot of a multi-shot vertical {format} ad for {name}, and it must read as "
    "scroll-stopping, organic user-generated content that a real Indian customer just pulled out "
    "their own phone to film — candid, handheld at arm's length or as a natural front-camera selfie "
    "(or a friend holding the phone just out of frame), slightly off-centre framing with gentle "
    "organic micro-shake, real autofocus hunt and only the available light of the room, the honest "
    "phone-shot feel of an Instagram/Facebook Reel testimonial you'd thumb-stop on, and never a "
    "glossy studio commercial or staged set. {anim}Shoot it {angle}, on a modern smartphone lens "
    "with a shallow but not cinematic depth of field and true-to-phone dynamic range. The on-camera "
    "presenter is {model}: treat this exact person as fixed and identical across every shot — same "
    "face, hair, skin and build — a real human with true-to-life skin texture, visible pores, fine "
    "flyaway hair, natural blemishes and honest, expressive eyes, absolutely never plastic, waxy, "
    "airbrushed, CGI or AI-looking and no beautify filter, with relaxed real energy, holding and "
    "naturally using the product the way a genuine owner would, turning its label toward the lens "
    "to show it off rather than posing like a paid model. Set it in {background}, a real, lived-in, "
    "authentically Indian home or everyday Indian location lit softly in natural available light "
    "with gentle window spill and the small imperfections of a real room — exactly where an "
    "ordinary person would actually record themselves, never a studio, seamless backdrop or "
    "artificial AI-looking set. The featured product must match the attached reference image "
    "EXACTLY — identical packaging/container format and proportions (never converted to a "
    "different container type: a jar stays a jar, never a tube), shape, colour, material, finish, "
    "label, logo and text — kept sharp and clearly in frame as the reason-to-believe hero moment, "
    "never redesigned, recoloured, relabelled or substituted. The presenter speaks straight into "
    "the phone in {language}, warmly "
    "and conversationally to camera, delivering exactly this line and nothing else: \"{line}\". "
    "LIP-SYNC IS THE SINGLE MOST IMPORTANT REQUIREMENT: mouth, lips, teeth, tongue and jaw must "
    "move in perfect frame-accurate sync with every single syllable, with natural co-articulation, "
    "micro-expressions, real blinking and small head movement, utterly indistinguishable from a "
    "real person genuinely speaking, with zero robotic, dubbed or out-of-sync feel, in ONE single "
    "identical voice across every shot — the same pitch, timbre, accent and pace, never a "
    "different-sounding voice between scenes — namely {voice} — speaking continuously with clean "
    "audio, no silence gaps or mid-word cut-offs, and no narration clutter. Strictly no on-screen "
    "text, subtitles, captions, "
    "logo overlays or watermark anywhere in frame.{colors_clause}"
)


def _veo_shot_prompt(brief, product, video, line: str, angle: str, has_seed: bool) -> str:
    """Full-depth UGC meta-ad shot brief for Veo 3.1 (see _VEO_PROMPT_TEMPLATE)."""
    name = brief.get("product_name") or product.name
    vmeta = video.meta or {}
    character = vmeta.get("character") or settings.veo_presenter
    voice = vmeta.get("voice") or settings.veo_voice
    setting_desc = vmeta.get("setting") or settings.veo_setting_bias
    anim = (
        "Animate the attached reference frame into a live, moving shot, keeping the presenter and "
        "product identical to it. " if has_seed else ""
    )
    colors = ", ".join((brief.get("brand_colors") or [])[:2])
    colors_clause = (
        f" Let subtle {colors} brand-colour accents sit naturally in the real setting."
        if colors else ""
    )
    # Cap the spoken line to what fits ONE ~8s clip at a natural pace (~18 words).
    # Cramming a long line into a short clip is the #1 cause of poor lip-sync.
    spoken = " ".join((line or "").split()[:18])
    return _VEO_PROMPT_TEMPLATE.format(
        format=video.format,
        name=name,
        model=character,
        voice=voice,
        background=setting_desc,
        line=spoken,
        angle=angle,
        language=settings.veo_language,
        anim=anim,
        colors_clause=colors_clause,
    )


async def begin_render(db: AsyncSession, product_id: str, video_id: str) -> tuple[GeneratedVideo, list[str]]:
    """Flip the video to 'rendering' and return at once — the minutes-long work runs
    in the background. The primary video is the Veo render (tagged 'Custom Model').
    Extra tagged SIBLING videos (one per extra model) are only spawned when the
    multi-model feature is switched on (settings.video_variants_enabled) AND a
    provider is configured — off by default, so Veo is the sole engine for now.
    Returns (primary, sibling_ids)."""
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    video.status = "rendering"
    video.progress = 5
    # NOTE: keep the existing video_url during the render — a failed re-render (e.g. a
    # Veo 429) must NOT destroy a previously good video. Success overwrites it below.
    meta = dict(video.meta or {})
    meta.setdefault("model_label", "Custom Model")  # Veo (our own pipeline)
    video.meta = meta
    await db.flush()

    sibling_ids: list[str] = []
    # Only the primary spawns siblings (variants never spawn their own), and only
    # when the multi-model feature is switched on. Off by default → Veo only.
    if settings.video_variants_enabled and higgsfield.enabled() and not meta.get("is_variant"):
        carry = {k: meta[k] for k in ("character", "voice", "setting", "frame_keys", "thumb_key") if k in meta}
        for mdef in higgsfield.models():
            sib = GeneratedVideo(
                product_id=video.product_id,
                idea_id=video.idea_id,
                duration=video.duration,
                format=video.format,
                script=video.script,
                voiceover=video.voiceover,
                storyboard=video.storyboard,
                captions=video.captions,
                transitions=video.transitions,
                frame_urls=list(video.frame_urls or []),
                thumbnail_url=video.thumbnail_url,
                status="rendering",
                progress=5,
                meta={**carry, "model_label": mdef.get("label"), "higgsfield": mdef,
                      "is_variant": True, "parent_id": video.id},
            )
            db.add(sib)
            await db.flush()
            sibling_ids.append(sib.id)

    await db.refresh(video)
    return video, sibling_ids


def _higgsfield_prompt(video, product) -> str:
    """Single-clip prompt for a Higgsfield model (image-to-video from frame 1)."""
    brief = assemble_brief(product, product.brand)
    name = brief.get("product_name") or product.name
    vmeta = video.meta or {}
    line = (video.voiceover or video.script or "").strip()[:500]
    return (
        f"Photorealistic {video.format} product advertisement for {name}. "
        f"Presenter: {vmeta.get('character') or settings.veo_presenter} — one consistent person. "
        f"Setting: a real, authentic Indian home / everyday Indian location — lived-in and "
        f"believable, never an artificial AI-looking backdrop. "
        f"Voice (single, consistent across the clip): {vmeta.get('voice') or settings.veo_voice}. "
        f"The presenter speaks to camera with accurate lip-sync in {settings.veo_language}: "
        f"\"{line}\". Keep the product EXACTLY as in the reference image (label, colours, shape). "
        f"Cinematic, natural lighting, real human skin — not CGI. No on-screen text or watermark."
    )


async def render_higgsfield_background(product_id: str, video_id: str) -> None:
    """Render a sibling video with its assigned Higgsfield model, in its own session."""
    from app.database.session import AsyncSessionLocal

    try:
        async with AsyncSessionLocal() as db:
            video = await db.get(GeneratedVideo, video_id)
            if not video:
                return
            product = await _load(db, product_id)
            mdef = (video.meta or {}).get("higgsfield")
            image_url = (video.frame_urls or [None])[0]
            mp4, reason = None, None
            if not mdef:
                reason = "No Higgsfield model assigned to this variant."
            elif not image_url:
                reason = "No public frame URL available to seed the video."
            else:
                mp4, reason = await higgsfield.generate_video(
                    mdef, _higgsfield_prompt(video, product), image_url
                )
            meta = dict(video.meta or {})
            if mp4:
                vkey = f"products/{product_id}/videos/{video_id[:8]}.mp4"
                video.video_url = storage.save_bytes(vkey, mp4)
                meta.update({"video_provider": "higgsfield", "has_audio": True, "video_key": vkey})
                meta.pop("render_error", None)
                frame = await media.extract_thumbnail(mp4, at_seconds=1.0)
                if frame:
                    tkey = f"products/{product_id}/videos/{video_id[:8]}-vthumb.jpg"
                    video.thumbnail_url = storage.save_bytes(tkey, frame)
                video.status = "ready"
            else:
                meta["render_error"] = reason or "Higgsfield render unavailable."
                video.status = "error"
            video.meta = meta
            video.progress = 100
            await db.commit()
    except Exception as exc:
        logger.exception("higgsfield render failed for %s", video_id)
        try:
            async with AsyncSessionLocal() as db:
                v = await db.get(GeneratedVideo, video_id)
                if v:
                    v.status = "error"
                    v.progress = 100
                    v.meta = {**(v.meta or {}), "render_error": str(exc)[:300]}
                    await db.commit()
        except Exception:
            logger.exception("could not mark higgsfield error for %s", video_id)


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
        meta.pop("render_error", None)  # clear any stale error from a prior failed run
        # Poster = a real frame from the rendered video (not the placeholder poster).
        frame = await media.extract_thumbnail(mp4, at_seconds=1.0)
        if frame:
            tkey = f"products/{product_id}/videos/{video_id[:8]}-vthumb.jpg"
            video.thumbnail_url = storage.save_bytes(tkey, frame)
            meta["thumb_key"] = tkey
    else:
        reason = media.last_video_error() or "Veo did not return any clips."
        if video.video_url:
            # A previous successful render exists — keep it. A failed re-render must
            # not downgrade a good video to the storyboard placeholder.
            meta["render_error"] = reason
        else:
            meta.update({
                "video_provider": "storyboard",
                "has_audio": False,
                "render_error": reason,
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
    scenes = list(video.storyboard or [])
    # One shot per generated frame, but never more than the configured cap (veo_shots).
    # Existing videos may carry more frames than the cap → use only the first N.
    cap = max(1, settings.veo_shots)
    n = min(len(frame_seeds), cap) if frame_seeds else cap
    split = _split_script(script_text, n)

    def _line_for(i: int) -> str:
        # Prefer the matching scene's own voiceover so each frame's shot stays on-script;
        # otherwise fall back to an even split of the full script.
        if i < len(scenes):
            sv = str(scenes[i].get("voiceover") or "").strip()
            if sv:
                return sv
        if split:
            return split[i] if i < len(split) else split[-1]
        return script_text

    # product_ref = the authentic product photo → passed to Veo as an ASSET reference so
    # the EXACT product appears in every shot (not just the composite seed frame).
    # Bounded concurrency + one retry per shot: firing every clip at once gets some Veo
    # calls rate-limited and silently dropped, which loses frames from the final reel.
    sem = asyncio.Semaphore(max(1, settings.veo_concurrency))

    async def _clip(i: int):
        seed = frame_seeds[i] if i < len(frame_seeds) else (frame_seeds[-1] if frame_seeds else model_seed)
        prompt = _veo_shot_prompt(
            brief, product, video, _line_for(i), _SHOT_ANGLES[i % len(_SHOT_ANGLES)], seed is not None
        )
        async with sem:
            # Single attempt: low concurrency already avoids the per-minute rate limit,
            # and retrying a hard quota (429) error just burns more quota for nothing.
            return await media.generate_video(
                prompt, video.format, image_bytes=seed, product_bytes=product_ref
            )

    results = await asyncio.gather(*[_clip(i) for i in range(n)])
    clips = [c for c in results if c]
    logger.info("Veo render: %d/%d shots succeeded for video %s", len(clips), n, video.id)
    # Record how many shots made the cut so it's visible/debuggable in the UI.
    video.meta = {**(video.meta or {}), "shots": f"{len(clips)}/{n}"}
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


async def restore(db: AsyncSession, video_id: str) -> GeneratedVideo:
    """Re-point a video at its rendered mp4 (from meta.video_key) if the file still
    exists — recovers a video whose DB url was cleared by a later failed render."""
    video = await db.get(GeneratedVideo, video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    meta = dict(video.meta or {})
    key = meta.get("video_key")
    if not (key and storage.exists(key)):
        raise HTTPException(
            status_code=400,
            detail="No recoverable video file for this reel — re-render it instead.",
        )
    video.video_url = storage.url_for(key)
    video.status = "ready"
    video.progress = 100
    meta.pop("render_error", None)
    if meta.get("video_provider") in (None, "storyboard"):
        meta["video_provider"] = "veo-multishot"
    meta["has_audio"] = True
    video.meta = meta
    await db.flush()
    await db.refresh(video)
    return video


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
