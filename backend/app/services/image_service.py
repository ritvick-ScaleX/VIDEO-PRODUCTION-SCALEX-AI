"""Image Generator.

Two flavours from the real product photo (via Nano Banana image editing):
  • white_background — clean e-commerce packshot on seamless white
  • creative        — vibrant lifestyle / poster creative
Falls back to Nano Banana text-to-image (no reference), then an on-brand Pillow
poster (fully offline). Model-agnostic `generate` — swap the backend anytime.
"""
from __future__ import annotations

import asyncio
import io
import textwrap
import uuid

import httpx
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.generation import GeneratedImage
from app.schemas.generation import ImageGenerateRequest
from app.services import analytics_service
from app.services.ai import media
from app.services.brief import assemble_brief
from app.services.product_service import _load
from app.storage import storage

FORMAT_DIMS: dict[str, tuple[int, int]] = {
    "square": (1080, 1080),
    "portrait": (1080, 1350),
    "landscape": (1200, 628),
    "story": (1080, 1920),
    "carousel": (1080, 1080),
    "poster": (1080, 1440),
    "lifestyle": (1200, 900),
}
_DEFAULT_COLORS = ["#6D5EF8", "#22D3EE", "#0B0B12"]


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    try:
        return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))  # type: ignore
    except Exception:
        return (109, 94, 248)


def _font(size: int, bold: bool = True):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _gradient(size: tuple[int, int], c1, c2) -> Image.Image:
    sw, sh = 64, 64
    small = Image.new("RGB", (sw, sh))
    px = small.load()
    for y in range(sh):
        for x in range(sw):
            t = ((x / sw) * 0.5 + (y / sh) * 0.5)
            px[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return small.resize(size, Image.BILINEAR)


def render_poster(fmt: str, headline: str, cta: str, brand_colors: list[str], brand_tag: str) -> bytes:
    w, h = FORMAT_DIMS.get(fmt, (1080, 1080))
    colors = (brand_colors or _DEFAULT_COLORS)[:2]
    if len(colors) < 2:
        colors = colors + _DEFAULT_COLORS
    c1, c2 = _hex_to_rgb(colors[0]), _hex_to_rgb(colors[1])
    img = _gradient((w, h), c1, c2)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle([0, int(h * 0.55), w, h], fill=(8, 8, 18, 150))
    draw.ellipse([int(w * 0.6), int(-h * 0.1), int(w * 1.1), int(h * 0.35)], fill=(255, 255, 255, 28))
    draw.ellipse([int(-w * 0.15), int(h * 0.5), int(w * 0.3), int(h * 0.95)], fill=(255, 255, 255, 20))
    pad = int(w * 0.08)
    draw.text((pad, pad), brand_tag.upper(), font=_font(max(20, int(w * 0.026))), fill=(255, 255, 255, 220))
    hl_size = max(44, int(w * 0.075))
    hl_font = _font(hl_size)
    lines = textwrap.wrap(headline or "Your headline here", width=max(12, int(w / (hl_size * 0.58))))[:4]
    line_h = int(hl_size * 1.18)
    y = int(h * 0.68) - (len(lines) * line_h) // 2
    for line in lines:
        draw.text((pad, y), line, font=hl_font, fill=(255, 255, 255, 255))
        y += line_h
    cta = cta or "Shop now"
    cta_font = _font(max(24, int(w * 0.032)))
    tb = draw.textbbox((0, 0), cta, font=cta_font)
    cta_w, cta_h = tb[2] - tb[0], tb[3] - tb[1]
    px, py = int(w * 0.05), int(h * 0.02)
    x0, y0 = pad, y + int(h * 0.03)
    x1, y1 = x0 + cta_w + px * 2, y0 + cta_h + py * 2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=(y1 - y0) // 2, fill=(255, 255, 255, 245))
    draw.text((x0 + px, y0 + py - tb[1]), cta, font=cta_font, fill=c1)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


_BAD_ASSET = ("logo", "icon", "favicon", "sprite", "placeholder", "loader", "badge", "payment")


def reference_pool(product) -> list[str]:
    """URLs the AI may use as references — the user's curated selection first.

    Without a selection, use ONLY the hero image: store pages list cross-sell
    products further down, and feeding those in gets the wrong product (and a
    hallucinated label) into generations.
    """
    selected = list(getattr(product, "selected_images", None) or [])
    if selected:
        return selected
    return list(product.images or [])[:1]


async def _fetch_one(client: httpx.AsyncClient, url: str) -> bytes | None:
    try:
        r = await client.get(url)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            if 6000 < len(r.content) < 12_000_000:
                return r.content
    except Exception:
        return None
    return None


def trim_solid_border(data: bytes, tolerance: int = 14) -> bytes:
    """Remove flat padding bands (white/black canvas) the model sometimes returns
    around the real composition. Returns original bytes if nothing to trim."""
    try:
        from PIL import ImageChops

        img = Image.open(io.BytesIO(data)).convert("RGB")
        w, h = img.size
        corners = [
            img.getpixel((1, 1)), img.getpixel((w - 2, 1)),
            img.getpixel((1, h - 2)), img.getpixel((w - 2, h - 2)),
        ]
        bg = max(set(corners), key=corners.count)
        diff = ImageChops.difference(img, Image.new("RGB", img.size, bg))
        diff = ImageChops.add(diff, diff, 2.0, -tolerance)
        bbox = diff.getbbox()
        # Only trim when a real composition remains and something was actually padded.
        if bbox and (bbox[2] - bbox[0]) > w * 0.4 and (bbox[3] - bbox[1]) > h * 0.4 and (
            bbox != (0, 0, w, h)
        ):
            img = img.crop(bbox)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            return buf.getvalue()
        return data
    except Exception:
        return data


def crop_to_aspect(data: bytes, target_w: int, target_h: int) -> bytes:
    """Centre-crop image bytes to a target aspect ratio (e.g. 9:16 for reels).

    Keeps frames/video seeds full-bleed — no letterboxing downstream. Returns the
    original bytes on any failure.
    """
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
        w, h = img.size
        target = target_w / target_h
        current = w / h
        if abs(current - target) < 0.01:
            return data
        if current > target:  # too wide → trim sides
            new_w = int(h * target)
            x0 = (w - new_w) // 2
            img = img.crop((x0, 0, x0 + new_w, h))
        else:  # too tall → trim top/bottom
            new_h = int(w / target)
            y0 = (h - new_h) // 2
            img = img.crop((0, y0, w, y0 + new_h))
        buf = io.BytesIO()
        img.convert("RGB").save(buf, format="PNG")
        return buf.getvalue()
    except Exception:
        return data


async def fetch_reference(urls: list[str]) -> bytes | None:
    """First usable PRODUCT image (skip logos/icons/tiny assets)."""
    ordered = [u for u in urls if not any(b in u.lower() for b in _BAD_ASSET)] or list(urls)
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        for url in ordered[:6]:
            data = await _fetch_one(client, url)
            if data:
                return data
    return None


async def fetch_references(urls: list[str], limit: int = 6) -> list[bytes]:
    """Download several usable product images (for varied generations)."""
    ordered = [u for u in urls if not any(b in u.lower() for b in _BAD_ASSET)] or list(urls)
    out: list[bytes] = []
    async with httpx.AsyncClient(follow_redirects=True, timeout=20) as client:
        for url in ordered[: limit * 2]:
            data = await _fetch_one(client, url)
            if data:
                out.append(data)
            if len(out) >= limit:
                break
    return out


_EDIT_PROMPTS = {
    "white_background": (
        "Re-photograph the SAME product as a premium e-commerce packshot on a pure seamless "
        "pure-white (#FFFFFF) studio background. Preserve the product EXACTLY — shape, colours, "
        "material, logo, text and every detail unchanged. Even, soft three-point softbox lighting; "
        "a natural soft contact shadow directly beneath; product perfectly centred, tack-sharp, "
        "true-to-life colour. Straight-on hero angle, full product in frame with clean margins. "
        "Ultra-detailed, high-resolution commercial catalogue quality. Absolutely no props, no "
        "text, no graphics, no watermark, no reflection clutter."
    ),
    # PRODUCT SHOT — the product alone is the hero, staged in a real environment.
    # Strictly NO people: no model, no hands, no body parts, no reflections of people.
    "product_shot": (
        "Create a premium product-hero photograph of the SAME product, kept EXACTLY identical "
        "(shape, colours, label, logo, text). The product is the ONLY subject, staged in a "
        "real-world scene that fits it (its natural habitat — e.g. sunscreen standing in warm "
        "sand with soft waves behind; a serum on wet stone with water ripples). "
        "STRICT RULE: absolutely NO people — no model, no hands, no fingers, no skin, no body "
        "parts, no human reflections or shadows. Natural props only. Golden natural light or "
        "controlled studio light, crisp macro detail on the product, shallow depth of field, "
        "85mm product-photography look, photorealistic. No text overlay, no watermark."
    ),
    # CREATIVE — lifestyle scene that ALWAYS features a real human model with the product.
    "creative": (
        "Create a high-end lifestyle advertising photograph with the SAME product as the hero, "
        "kept EXACTLY identical (shape, colours, label, logo, text). A real human model MUST "
        "feature prominently, naturally using, holding or wearing the product — ALWAYS include a "
        "believable person in the scene even if the concept/brief does not explicitly mention one; "
        "pick a model who fits the product and its audience. REALISM IS CRITICAL: this must look like "
        "an actual photograph of a real person — natural skin with visible pores and fine texture, "
        "subtle skin imperfections, real hair strands (flyaways included), natural asymmetric "
        "features, believable hands, honest catch-lights in the eyes. NOT retouched-plastic, NOT "
        "airbrushed, NOT CGI, NOT doll-like, no beauty-filter smoothing, no waxy or porcelain "
        "skin. Candid editorial energy, cinematic natural lighting with soft key and gentle rim, "
        "rich but true colour grade, shallow depth of field, 35mm documentary-commercial look. "
        "Leave clean negative space for a headline. No text, no watermark."
    ),
}
_TEXT_PROMPTS = {
    "white_background": (
        "Premium e-commerce packshot of {name} on a pure seamless white (#FFFFFF) studio "
        "background, soft even softbox lighting, natural contact shadow, centred and tack-sharp, "
        "true-to-life colours, high-resolution catalogue quality, no text, no props, no watermark"
    ),
    "product_shot": (
        "Premium product-hero photograph of {name} staged alone in a fitting real-world scene, "
        "product is the only subject, absolutely no people, no hands, no body parts, natural "
        "props and light, crisp macro product detail, shallow depth of field, 85mm look, "
        "photorealistic, no text, no watermark"
    ),
    "creative": (
        "High-end lifestyle advertising photograph featuring {name} as the hero, ALWAYS with a "
        "real human model using/holding/wearing it naturally (include a person even if not "
        "mentioned) — natural skin texture with visible pores, real hair, candid "
        "editorial energy, not airbrushed, not CGI, not plastic — cinematic natural lighting, "
        "rich true colour grade, shallow depth of field, negative space for a headline, "
        "photorealistic, no text, no watermark"
    ),
}


def _facts_block(product, brief) -> str:
    """Grounding facts so scenes match the actual product (its world, actives, buyer)."""
    parts = [f"PRODUCT: {product.name}."]
    if product.description:
        parts.append(f"About: {product.description[:280]}")
    if product.ingredients:
        parts.append(f"Key ingredients/actives: {', '.join(product.ingredients[:8])}.")
    if product.benefits:
        parts.append(f"Benefits: {'; '.join(product.benefits[:4])}.")
    audience = product.target_audience or brief.get("customer_persona")
    if audience:
        parts.append(f"Target audience: {str(audience)[:200]}")
    return " ".join(parts)


async def _rejection_feedback(db: AsyncSession, product_id: str, limit: int = 5) -> list[str]:
    """Comments from recently rejected images — the avoid-list for the next run."""
    rows = await db.execute(
        select(GeneratedImage.review_comment)
        .where(
            GeneratedImage.product_id == product_id,
            GeneratedImage.review_status == "rejected",
            GeneratedImage.review_comment.is_not(None),
            GeneratedImage.review_comment != "",
        )
        .order_by(GeneratedImage.updated_at.desc())
        .limit(limit)
    )
    return [c for (c,) in rows.all() if c]


async def generate(db: AsyncSession, product_id: str, req: ImageGenerateRequest) -> list[GeneratedImage]:
    product = await _load(db, product_id)
    brief = assemble_brief(product, product.brand)
    brand_colors = brief.get("brand_colors") or _DEFAULT_COLORS
    brand_tag = product.name
    headline = req.headline or (brief.get("hooks") or [None])[0] or brief.get("usp") or product.name
    cta = req.cta or brief.get("cta") or "Shop now"
    cat = req.category

    # Use the user's curated selection as references; fall back to all scraped images.
    refs: list[bytes] = []
    if media.images_enabled():
        pool = reference_pool(product)
        if pool:
            refs = await fetch_references(pool, limit=max(req.count, 4))

    # Compose the prompt: category direction + product facts + chosen market angle
    # + user's extra direction + avoid-list from rejected-image feedback.
    fmt_w, fmt_h = FORMAT_DIMS.get(req.format, (1080, 1080))
    blocks: list[str] = [
        _EDIT_PROMPTS.get(cat, _EDIT_PROMPTS["creative"]),
        _facts_block(product, brief),
        (
            f"CANVAS: compose for a {req.format} frame ({fmt_w}x{fmt_h}); fill the ENTIRE canvas "
            "edge-to-edge with the scene — no borders, no letterboxing, no blank margins, no "
            "white padding bands."
        ),
        (
            "LABEL FIDELITY: reproduce the product's label, typography, colours and packaging "
            "EXACTLY as in the reference photo — never invent, rewrite, translate or garble any "
            "label text."
        ),
    ]
    idea = None
    if req.idea_id:
        from app.models.idea import Idea

        idea = await db.get(Idea, req.idea_id)
    if idea is not None:
        blocks.append(
            "CONCEPT TO EXECUTE — build the scene from this market angle: "
            f"“{idea.title}” ({idea.angle}). Scene: {idea.description} "
            + (f"Mood/hook: “{idea.hook}”." if idea.hook else "")
        )
    if req.prompt:
        blocks.append(f"EXTRA DIRECTION from the user (must follow): {req.prompt.strip()}")
    feedback = await _rejection_feedback(db, product_id)
    if feedback:
        blocks.append(
            "USER FEEDBACK — earlier images were REJECTED for the reasons below. "
            "Do not repeat these mistakes:\n- " + "\n- ".join(f[:200] for f in feedback)
        )

    edit_prompt = "\n\n".join(blocks)
    text_prompt = "\n\n".join(
        [_TEXT_PROMPTS.get(cat, _TEXT_PROMPTS["creative"]).format(name=product.name), *blocks[1:]]
    )

    async def _one(i: int) -> tuple[bytes, str]:
        """Produce one image (the slow AI part). Run concurrently across the batch."""
        data = None
        provider = "template"
        ref = refs[i % len(refs)] if refs else None  # rotate through selected images
        if ref is not None:
            data = await media.edit_image(ref, edit_prompt)
            if data:
                provider = "nano-banana"
        if data is None and media.images_enabled():
            data = await media.generate_image(text_prompt, req.format)
            if data:
                provider = "nano-banana"
        if data is None:
            rotated = brand_colors[i % len(brand_colors):] + brand_colors[: i % len(brand_colors)]
            data = render_poster(req.format, headline, cta, rotated, brand_tag)
            provider = "template"
        if provider != "template":
            # Kill padding bands the model sometimes returns, then enforce the
            # requested format's exact aspect (e.g. 9:16 for story) so the image
            # is always full-bleed at the right ratio.
            data = trim_solid_border(data)
            data = crop_to_aspect(data, fmt_w, fmt_h)
        return data, provider

    # Generate the whole batch CONCURRENTLY — a sequential loop was slow enough to
    # exceed the edge proxy timeout, so images only appeared after a manual refresh.
    results = await asyncio.gather(*[_one(i) for i in range(req.count)])

    created: list[GeneratedImage] = []
    w, h = FORMAT_DIMS.get(req.format, (1080, 1080))
    for i, (data, provider) in enumerate(results):
        key = f"products/{product_id}/images/{cat}-{product_id[:8]}-{i}-{uuid.uuid4().hex[:8]}.png"
        url = storage.save_bytes(key, data)
        img = GeneratedImage(
            product_id=product_id,
            category=cat,
            format=req.format,
            prompt=req.prompt or (idea.title if idea is not None else headline),
            url=url,
            width=w,
            height=h,
            meta={
                "provider": provider,
                "storage_key": key,
                "cta": cta,
                "idea_id": req.idea_id,
                "idea_title": idea.title if idea is not None else None,
                "feedback_applied": len(feedback),
                # Why it fell back to the template renderer (for debugging live).
                "image_error": media.last_image_error() if provider == "template" else None,
            },
        )
        db.add(img)
        created.append(img)

    await db.flush()
    await analytics_service.record_event(
        db, "image_generated", brand_id=product.brand_id, product_id=product_id,
        meta={"category": cat, "format": req.format, "count": req.count},
    )
    for img in created:
        await db.refresh(img)
    return created


async def list_for_product(db: AsyncSession, product_id: str) -> list[GeneratedImage]:
    rows = await db.execute(
        select(GeneratedImage)
        .where(GeneratedImage.product_id == product_id)
        .order_by(GeneratedImage.created_at.desc())
    )
    return list(rows.scalars().all())


async def set_saved(db: AsyncSession, image_id: str, saved: bool) -> GeneratedImage | None:
    obj = await db.get(GeneratedImage, image_id)
    if obj:
        obj.is_saved = saved
        await db.flush()
    return obj


async def set_review(
    db: AsyncSession, image_id: str, status: str, comment: str | None
) -> GeneratedImage | None:
    """Accept/reject an image. Rejection comments become avoid-context for future runs."""
    obj = await db.get(GeneratedImage, image_id)
    if obj:
        obj.review_status = status
        obj.review_comment = (comment or "").strip() or None
        await db.flush()
        await db.refresh(obj)
    return obj


async def delete(db: AsyncSession, image_id: str) -> None:
    obj = await db.get(GeneratedImage, image_id)
    if obj:
        key = obj.meta.get("storage_key") if obj.meta else None
        if key:
            try:
                storage.delete(key)
            except Exception:
                pass
        await db.delete(obj)
        await db.flush()
