"""Image Generator.

Two flavours from the real product photo (via Nano Banana image editing):
  • white_background — clean e-commerce packshot on seamless white
  • creative        — vibrant lifestyle / poster creative
Falls back to Nano Banana text-to-image (no reference), then an on-brand Pillow
poster (fully offline). Model-agnostic `generate` — swap the backend anytime.
"""
from __future__ import annotations

import io
import textwrap

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
    """URLs the AI may use as references — the user's curated selection first."""
    selected = list(getattr(product, "selected_images", None) or [])
    if selected:
        return selected
    return list(product.images or [])


async def _fetch_one(client: httpx.AsyncClient, url: str) -> bytes | None:
    try:
        r = await client.get(url)
        if r.status_code == 200 and r.headers.get("content-type", "").startswith("image"):
            if 6000 < len(r.content) < 12_000_000:
                return r.content
    except Exception:
        return None
    return None


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
    "creative": (
        "Create a high-end advertising campaign photograph with the SAME product as the hero. "
        "Keep the product identical and photorealistic. Art-direct a tasteful, story-driven "
        "lifestyle scene that fits the product and brand; cinematic lighting with a soft key and "
        "gentle rim light, rich but natural colour grade, shallow depth of field with pleasing "
        "bokeh. Leave clean negative space for a headline. Editorial magazine quality, 35mm look, "
        "photorealistic. No text, no logos-overlay, no watermark."
    ),
    "product_shot": (
        "Create a premium studio hero shot of the SAME product, kept identical. Dramatic yet "
        "controlled key-plus-fill lighting, elegant subtle gradient backdrop, a soft reflection "
        "on a smooth surface, crisp macro detail and glossy commercial finish. 85mm lens look, "
        "tasteful composition. High-end, photorealistic. No text, no watermark."
    ),
}
_TEXT_PROMPTS = {
    "white_background": (
        "Premium e-commerce packshot of {name} on a pure seamless white (#FFFFFF) studio "
        "background, soft even softbox lighting, natural contact shadow, centred and tack-sharp, "
        "true-to-life colours, high-resolution catalogue quality, no text, no props, no watermark"
    ),
    "creative": (
        "High-end advertising campaign photograph featuring {name} as the hero in an art-directed "
        "lifestyle scene, cinematic lighting, rim light, rich natural colour grade, shallow depth "
        "of field with bokeh, negative space for a headline, editorial magazine quality, "
        "photorealistic, no text, no watermark"
    ),
    "product_shot": (
        "Premium studio hero shot of {name}, dramatic key-plus-fill lighting, subtle gradient "
        "backdrop, soft reflection, crisp macro detail, glossy commercial finish, 85mm lens look, "
        "photorealistic, no text, no watermark"
    ),
}


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

    edit_prompt = req.prompt or _EDIT_PROMPTS.get(cat, _EDIT_PROMPTS["creative"])
    text_prompt = req.prompt or _TEXT_PROMPTS.get(cat, _TEXT_PROMPTS["creative"]).format(name=product.name)

    created: list[GeneratedImage] = []
    for i in range(req.count):
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

        key = f"products/{product_id}/images/{cat}-{product_id[:8]}-{i}-{len(created)}-{abs(hash(edit_prompt)) % 100000}.png"
        url = storage.save_bytes(key, data)
        w, h = FORMAT_DIMS.get(req.format, (1080, 1080))
        img = GeneratedImage(
            product_id=product_id,
            category=cat,
            format=req.format,
            prompt=req.prompt or headline,
            url=url,
            width=w,
            height=h,
            meta={"provider": provider, "storage_key": key, "cta": cta},
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
