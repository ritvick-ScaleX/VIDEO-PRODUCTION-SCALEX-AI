"""Website scraper.

Renders the page with Playwright when available, falls back to an httpx GET,
then extracts product signals with BeautifulSoup. Everything degrades
gracefully — if a strategy is unavailable the next one runs; if all fail the
project is left ready for manual editing.
"""
from __future__ import annotations

import re
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.product import Product
from app.services import analytics_service

logger = get_logger(__name__)

_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0 Safari/537.36"
)
_PRICE_RE = re.compile(r"(?:[$£€]|USD|EUR|GBP)\s?\d[\d,]*(?:\.\d{2})?", re.I)
_HEX_RE = re.compile(r"#[0-9a-fA-F]{6}")


async def _fetch_html(url: str) -> str:
    """Prefer Playwright (JS-rendered); fall back to a plain HTTP GET."""
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(user_agent=_UA)
            await page.goto(url, wait_until="networkidle", timeout=30000)
            html = await page.content()
            await browser.close()
            logger.info("scraped via Playwright: %s", url)
            return html
    except Exception as exc:
        logger.info("Playwright unavailable/failed (%s) — httpx fallback", exc)

    import httpx

    async with httpx.AsyncClient(
        headers={"User-Agent": _UA}, follow_redirects=True, timeout=20
    ) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


def _abs(base: str, src: str | None) -> str | None:
    if not src:
        return None
    return urljoin(base, src)


def parse_html(html: str, base_url: str) -> dict[str, Any]:
    # Prefer lxml; fall back to the stdlib parser if it isn't installed.
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    def meta(prop: str, attr: str = "property") -> str | None:
        tag = soup.find("meta", attrs={attr: prop})
        return tag.get("content") if tag and tag.get("content") else None

    title = (
        meta("og:title")
        or (soup.title.string.strip() if soup.title and soup.title.string else None)
    )
    site_name = meta("og:site_name")
    description = meta("description", "name") or meta("og:description")
    hero = soup.find("h1")
    hero_content = hero.get_text(strip=True) if hero else None

    # Images — collect, then drop non-product assets (logos, icons, sprites).
    def _skip(u: str) -> bool:
        low = u.lower()
        return low.endswith(".svg") or any(
            b in low for b in ("logo", "icon", "favicon", "sprite", "placeholder", "loader", "badge", "payment")
        )

    images: list[str] = []
    for img in soup.find_all("img")[:40]:
        src = img.get("src") or img.get("data-src") or img.get("data-srcset", "").split(" ")[0]
        u = _abs(base_url, src)
        if u and u not in images and not _skip(u):
            images.append(u)
    og_img = meta("og:image")
    if og_img:
        og_abs = _abs(base_url, og_img)
        if og_abs and not _skip(og_abs):
            images.insert(0, og_abs)  # og:image is usually the hero product shot
    # de-dupe preserving order
    seen: set[str] = set()
    images = [i for i in images if i and not (i in seen or seen.add(i))][:12]

    # Logo / brand icon — prefer a clean, square-ish asset good as a profile icon:
    #   1. apple-touch-icon (opaque, high-res square)
    #   2. a header/nav <img> that looks like the brand logo
    #   3. og:image:logo / <link rel=...icon> favicon as a last resort
    logo = None
    apple = soup.find("link", rel=lambda v: v and "apple-touch-icon" in v.lower())
    if apple and apple.get("href"):
        logo = _abs(base_url, apple.get("href"))
    if not logo:
        logo_img = soup.find("img", attrs={"alt": re.compile("logo", re.I)}) or soup.find(
            "img", src=re.compile("logo", re.I)
        )
        if logo_img and logo_img.get("src"):
            logo = _abs(base_url, logo_img.get("src"))
    if not logo:
        icon = soup.find("link", rel=lambda v: v and "icon" in v.lower())
        if icon and icon.get("href"):
            logo = _abs(base_url, icon.get("href"))

    # Features / benefits from list items
    features: list[str] = []
    for li in soup.find_all("li")[:40]:
        text = li.get_text(" ", strip=True)
        if 8 <= len(text) <= 120:
            features.append(text)
    features = features[:8]

    # Price
    price = None
    m = _PRICE_RE.search(soup.get_text(" ", strip=True))
    if m:
        price = m.group(0)

    # Brand colors: theme-color + hex codes found in inline styles
    colors: list[str] = []
    theme = meta("theme-color", "name")
    if theme and _HEX_RE.fullmatch(theme.strip()):
        colors.append(theme.strip())
    for style in soup.find_all(style=True)[:60]:
        for hexc in _HEX_RE.findall(style.get("style", "")):
            if hexc.lower() not in [c.lower() for c in colors]:
                colors.append(hexc)
    colors = colors[:5] or ["#6D5EF8", "#22D3EE", "#0B0B12"]

    return {
        "title": title,
        "site_name": site_name,
        "description": description,
        "hero_content": hero_content,
        "images": images,
        "logo_url": logo,
        "features": features,
        "price": price,
        "brand_colors": colors,
        "site": urlparse(base_url).netloc,
    }


async def scrape_into_brand(db: AsyncSession, brand) -> dict[str, Any]:
    """Scrape a brand homepage into the brand's identity fields (name, logo, colours, voice)."""
    from app.prompts import brand as brand_prompt
    from app.services import mocks
    from app.services.ai import llm

    url = brand.website
    html = await _fetch_html(url)
    data = parse_html(html, url)

    # Clean brand name: og:site_name → title before a separator → hostname.
    raw_name = data.get("site_name") or data.get("title") or urlparse(url).netloc
    clean_name = re.split(r"\s[|\-–—:·]\s", raw_name)[0].strip() if raw_name else raw_name

    signals = {
        "name": clean_name,
        "site_name": data.get("site_name"),
        "title": data.get("title"),
        "description": data.get("description"),
        "hero_content": data.get("hero_content"),
        "tagline": data.get("hero_content"),
        "features": data.get("features"),
        "brand_colors": data.get("brand_colors"),
        "site": data.get("site"),
    }

    enriched = await llm.generate_structured(
        system=brand_prompt.SYSTEM,
        prompt=brand_prompt.build_prompt(signals),
        schema=brand_prompt.SCHEMA,
        mock=lambda: mocks.mock_brand(signals),
    )

    # Only fill fields the user hasn't already set.
    if not brand.name or brand.name in ("New brand", "Brand", data.get("site")):
        brand.name = enriched.get("name") or clean_name or brand.name
    brand.logo_url = brand.logo_url or data.get("logo_url")
    if not brand.brand_colors:
        brand.brand_colors = data.get("brand_colors", [])
    brand.tagline = brand.tagline or enriched.get("tagline")
    brand.mission = brand.mission or enriched.get("mission")
    brand.brand_voice = brand.brand_voice or enriched.get("brand_voice")
    brand.writing_style = brand.writing_style or enriched.get("writing_style")
    brand.target_audience = brand.target_audience or enriched.get("target_audience")
    meta = dict(brand.meta or {})
    meta["scrape"] = {"url": url, "site": data.get("site"), "logo_url": data.get("logo_url")}
    brand.meta = meta

    await db.flush()
    await analytics_service.record_event(
        db, "brand_scraped", brand_id=brand.id, meta={"url": url}
    )
    return {**data, **enriched}


async def scrape_into_product(db: AsyncSession, product: Product) -> dict[str, Any]:
    """Scrape the product's URL into its fields; seed the brand identity if empty."""
    url = product.source_url
    html = await _fetch_html(url)
    data = parse_html(html, url)

    product.name = product.name or data.get("title") or "Product"
    product.description = product.description or data.get("description")
    product.hero_content = product.hero_content or data.get("hero_content")
    product.images = data.get("images") or product.images
    product.logo_url = product.logo_url or data.get("logo_url")
    product.features = data.get("features") or product.features
    product.price = product.price or data.get("price")
    product.brand_colors = data.get("brand_colors") or product.brand_colors
    product.raw_scrape = data
    if data.get("images"):
        product.thumbnail_url = data["images"][0]

    # Seed brand identity from the scrape when the brand is still bare.
    brand = product.brand
    if brand is not None:
        if not brand.brand_colors:
            brand.brand_colors = data.get("brand_colors", [])
        if not brand.logo_url:
            brand.logo_url = data.get("logo_url")

    await db.flush()
    await analytics_service.record_event(
        db, "scrape_completed", brand_id=product.brand_id, product_id=product.id,
        meta={"url": url, "images": len(data.get("images", []))},
    )
    return data
