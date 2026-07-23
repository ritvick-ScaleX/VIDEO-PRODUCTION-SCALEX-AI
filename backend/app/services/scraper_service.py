"""Website scraper.

Renders the page with Playwright when available, falls back to an httpx GET,
then extracts product signals with BeautifulSoup. Everything degrades
gracefully — if a strategy is unavailable the next one runs; if all fail the
project is left ready for manual editing.
"""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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


_HEADERS = {
    "User-Agent": _UA,
    # Browser-like headers so stores are less likely to serve a bot-challenge page.
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


async def _fetch_html(url: str, use_proxy: bool = False) -> str:
    """Fetch page HTML. Direct (Playwright → httpx) by default; through the configured
    proxy (e.g. Bright Data) when use_proxy=True. Returns "" on any failure (never
    raises) so callers can fall through the tiers: direct → proxy → manual upload."""
    import httpx

    if use_proxy:
        # Preferred: Bright Data Scraping Browser (remote Chrome over CDP) — renders JS
        # and auto-solves bot challenges. connect_over_cdp talks to a REMOTE browser, so
        # it needs no local chromium binary (works on a bare server).
        ws = settings.scalex_browser_ws.strip()
        if ws:
            try:
                from playwright.async_api import async_playwright

                async with async_playwright() as p:
                    browser = await p.chromium.connect_over_cdp(ws, timeout=60000)
                    try:
                        page = await browser.new_page()
                        await page.goto(url, wait_until="domcontentloaded", timeout=90000)
                        html = await page.content()
                    finally:
                        await browser.close()
                logger.info("scraped via Scraping Browser: %s", url)
                return html
            except Exception as exc:
                logger.info("scraping-browser fetch failed (%s)", exc)
                # fall through to an HTTP proxy if one is also configured
        # Fallback: a plain HTTP proxy (residential / unlocker) via httpx.
        proxy = settings.scraper_proxy_url.strip()
        if not proxy:
            return ""
        try:
            # verify=False: unlocker proxies often MITM TLS; fine for scraping.
            async with httpx.AsyncClient(
                proxy=proxy, verify=False, headers=_HEADERS, follow_redirects=True, timeout=45
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                logger.info("scraped via proxy: %s", url)
                return resp.text
        except Exception as exc:
            logger.info("proxy fetch failed (%s)", exc)
            return ""

    # Direct — prefer Playwright (JS-rendered), else a plain HTTP GET.
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
    try:
        async with httpx.AsyncClient(headers=_HEADERS, follow_redirects=True, timeout=25) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.text
    except Exception as exc:
        logger.info("direct fetch failed (%s)", exc)
        return ""


def _abs(base: str, src: str | None) -> str | None:
    if not src:
        return None
    return _force_https(urljoin(base, src))


def _force_https(u: str | None) -> str | None:
    """Normalise to https (handle protocol-relative //… and http://) so images aren't
    blocked as mixed content on our https app."""
    if not u:
        return None
    u = u.strip()
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("http://"):
        return "https://" + u[len("http://"):]
    return u


def _largest_from_srcset(srcset: str | None) -> str | None:
    """Pick the highest-resolution URL from a srcset / data-srcset attribute."""
    if not srcset:
        return None
    best, best_w = None, -1
    for part in srcset.split(","):
        bits = part.strip().split()
        if not bits:
            continue
        w = 0
        if len(bits) > 1 and bits[1].endswith("w"):
            try:
                w = int(bits[1][:-1])
            except ValueError:
                w = 0
        if w >= best_w:
            best, best_w = bits[0], w
    return best


def _jsonld_images(soup: BeautifulSoup) -> list[str]:
    """Product images from schema.org JSON-LD — platform-agnostic, clean URLs."""
    out: list[str] = []
    for tag in soup.find_all("script", attrs={"type": "application/ld+json"}):
        raw = tag.string or tag.get_text() or ""
        try:
            data = json.loads(raw)
        except Exception:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
                continue
            if not isinstance(node, dict):
                continue
            if isinstance(node.get("@graph"), list):
                stack.extend(node["@graph"])
            t = node.get("@type", "")
            t = ",".join(t) if isinstance(t, list) else str(t)
            if "Product" not in t:
                continue
            img = node.get("image")
            if isinstance(img, str):
                out.append(img)
            elif isinstance(img, list):
                for x in img:
                    if isinstance(x, str):
                        out.append(x)
                    elif isinstance(x, dict) and x.get("url"):
                        out.append(x["url"])
            elif isinstance(img, dict) and img.get("url"):
                out.append(img["url"])
    return out


async def _fetch_product_images(url: str, use_proxy: bool = False) -> list[str]:
    """Clean product images from a store's data API (Shopify /products/{h}.json|.js).

    A lightweight JSON endpoint that dodges the JS/bot-challenge pages that block HTML
    scraping from datacenter IPs, and returns full-resolution, product-only images.
    Routed through the proxy when use_proxy=True. Returns [] on any failure.
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.rstrip("/")
        if "/products/" not in path:
            return []
        origin = f"{parsed.scheme}://{parsed.netloc}"
        import httpx

        headers = {"User-Agent": _UA, "Accept": "application/json, text/javascript, */*"}
        client_kw: dict[str, Any] = dict(headers=headers, follow_redirects=True, timeout=20)
        if use_proxy:
            proxy = settings.scraper_proxy_url.strip()
            if not proxy:
                return []
            client_kw.update(proxy=proxy, verify=False)
        async with httpx.AsyncClient(**client_kw) as c:
            for suffix in (".json", ".js"):
                try:
                    r = await c.get(f"{origin}{path}{suffix}")
                    if r.status_code != 200:
                        continue
                    data = r.json()
                except Exception:
                    continue
                prod = data.get("product") if isinstance(data, dict) else None
                if not isinstance(prod, dict):
                    continue
                out: list[str] = []
                for im in prod.get("images") or []:
                    src = im.get("src") if isinstance(im, dict) else (im if isinstance(im, str) else None)
                    src = _force_https(src)
                    if src:
                        out.append(src)
                if out:
                    logger.info("scraped %d images via store JSON API: %s", len(out), url)
                    return out
    except Exception as exc:
        logger.info("product JSON image fetch failed (%s)", exc)
    return []


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
    # 1) Hero from og:image / twitter:image (usually the main product shot).
    for hero_meta in (meta("og:image:secure_url"), meta("og:image"), meta("twitter:image", "name")):
        h = _abs(base_url, hero_meta)
        if h and not _skip(h):
            images.append(h)
    # 2) schema.org JSON-LD Product images (platform-agnostic, clean URLs).
    for u in _jsonld_images(soup):
        u = _abs(base_url, u)
        if u and not _skip(u):
            images.append(u)
    # 3) <img> tags — prefer the largest srcset entry; skip data-URI lazy placeholders.
    for img in soup.find_all("img")[:60]:
        cand = (
            _largest_from_srcset(img.get("srcset"))
            or _largest_from_srcset(img.get("data-srcset"))
            or img.get("src")
            or img.get("data-src")
        )
        if not cand or cand.startswith("data:"):
            continue
        u = _abs(base_url, cand)
        if u and not _skip(u):
            images.append(u)
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

    # Tier 1 — direct fetch.
    html = await _fetch_html(url)
    data = parse_html(html, url) if html else {"images": []}
    api_imgs = await _fetch_product_images(url)
    if api_imgs:
        seen = set(api_imgs)
        data["images"] = (api_imgs + [i for i in (data.get("images") or []) if i not in seen])[:12]

    # Tier 2 — if the site blocked our IP (nothing came back), retry through Bright Data.
    blocked = not data.get("images") and not (data.get("title") or "").strip()
    if blocked and (settings.scalex_browser_ws.strip() or settings.scraper_proxy_url.strip()):
        logger.info("direct scrape empty — retrying via Bright Data: %s", url)
        phtml = await _fetch_html(url, use_proxy=True)
        pdata = parse_html(phtml, url) if phtml else {}
        papi = await _fetch_product_images(url, use_proxy=True)
        merged = papi + [i for i in (pdata.get("images") or []) if i not in set(papi)]
        if merged:
            pdata["images"] = merged[:12]
        if pdata.get("images") or (pdata.get("title") or "").strip():
            data = pdata  # proxy got real content — use it

    # The page's real title beats the URL-slug guess the client sent at create time.
    scraped_title = (data.get("title") or "").strip()
    if scraped_title:
        clean = re.split(r"\s+[|–—-]\s+", scraped_title)[0].strip() or scraped_title
        product.name = clean[:255]
    else:
        product.name = product.name or "Product"
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
