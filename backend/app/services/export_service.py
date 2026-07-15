"""Export Center service — PDF summaries, ZIP packages, PNG/JPG, video bundles."""
from __future__ import annotations

import io
import zipfile

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models.export import Export
from app.schemas.export import ExportCreate
from app.services import (
    analytics_service,
    copy_service,
    image_service,
    scoring_service,
    video_service,
)
from app.services.product_service import _load
from app.storage import storage

logger = get_logger(__name__)


def _build_summary_pdf(product, copies, scores) -> bytes:
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

    brand = product.brand if product else None
    title = product.name if product else "Campaign"
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title=f"{title} — Campaign Summary")
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("H1", parent=styles["Title"], fontSize=22, spaceAfter=6)
    sub = ParagraphStyle("Sub", parent=styles["Normal"], textColor="#6D5EF8", fontSize=11)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=14, spaceBefore=14)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5, leading=15, alignment=TA_LEFT)

    story = [
        Paragraph(title, h1),
        Paragraph(f"ScaleX AI · {brand.name if brand else ''} · Campaign Summary", sub),
        Spacer(1, 0.4 * cm),
    ]
    if product:
        story.append(Paragraph("Product", h2))
        if product.description:
            story.append(Paragraph(product.description, body))
        if product.benefits:
            story.append(Paragraph("Benefits: " + ", ".join(product.benefits), body))
        analysis = product.analysis or {}
        if analysis.get("usp"):
            story.append(Paragraph(f"<b>USP:</b> {analysis['usp']}", body))
        if analysis.get("strategy_summary"):
            story.append(Paragraph("Strategy", h2))
            story.append(Paragraph(analysis["strategy_summary"], body))
    if copies:
        story.append(Paragraph("Ad Copy", h2))
        for c in copies[:8]:
            story.append(Paragraph(f"<b>[{c.platform}/{c.tone}]</b> {c.headline or ''}", body))
            if c.body:
                story.append(Paragraph(c.body, body))
            story.append(Spacer(1, 0.2 * cm))
    if scores:
        story.append(Paragraph("Creative Scores", h2))
        for s in scores[:6]:
            story.append(Paragraph(f"{s.target_type.title()} — overall {s.overall}/100", body))
    doc.build(story)
    return buf.getvalue()


async def create_export(db: AsyncSession, req: ExportCreate) -> Export:
    pid = req.product_id
    product = await _load(db, pid) if pid else None
    copies = await copy_service.list_for_product(db, pid) if pid else []
    images = await image_service.list_for_product(db, pid) if pid else []
    videos = await video_service.list_for_product(db, pid) if pid else []
    scores = await scoring_service.list_for_product(db, pid) if pid else []

    label = req.label or (f"{product.name} " if product else "") + f"{req.kind.upper()} export"
    base_key = f"exports/{pid or 'campaign'}"
    data: bytes
    key: str
    meta: dict = {}

    if req.kind == "pdf":
        data = _build_summary_pdf(product, copies, scores)
        key = f"{base_key}/summary-{abs(hash(label)) % 100000}.pdf"

    elif req.kind in {"png", "jpg"}:
        target = None
        if req.asset_ids:
            target = next((img for img in images if img.id in req.asset_ids), None)
        target = target or (images[0] if images else None)
        if target and target.meta and target.meta.get("storage_key"):
            raw = storage.read_bytes(target.meta["storage_key"])
        else:
            raw = image_service.render_poster(
                "square", product.name if product else "Campaign", "Shop now",
                (product.brand_colors if product else None) or ["#6D5EF8", "#22D3EE"],
                product.name if product else "Campaign",
            )
        if req.kind == "jpg":
            from PIL import Image

            im = Image.open(io.BytesIO(raw)).convert("RGB")
            out = io.BytesIO()
            im.save(out, format="JPEG", quality=92)
            data = out.getvalue()
        else:
            data = raw
        key = f"{base_key}/creative-{abs(hash(label)) % 100000}.{req.kind}"

    elif req.kind == "mp4":
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for v in videos:
                zf.writestr(f"{v.id}/script.txt", v.script or "")
                zf.writestr(f"{v.id}/voiceover.txt", v.voiceover or "")
                zf.writestr(f"{v.id}/captions.txt", "\n".join(v.captions or []))
                vk = (v.meta or {}).get("video_key")
                if vk and storage.exists(vk):
                    zf.writestr(f"{v.id}/video.mp4", storage.read_bytes(vk))
                elif v.meta and v.meta.get("thumb_key") and storage.exists(v.meta["thumb_key"]):
                    zf.writestr(f"{v.id}/thumbnail.png", storage.read_bytes(v.meta["thumb_key"]))
        data = buf.getvalue()
        key = f"{base_key}/video-package-{abs(hash(label)) % 100000}.zip"
        meta = {"note": "Video package (MP4 if rendered, else script + thumbnail)."}

    else:  # zip — full campaign
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            if product:
                zf.writestr("summary.pdf", _build_summary_pdf(product, copies, scores))
            copy_txt = "\n\n".join(
                f"[{c.platform}/{c.tone}]\n{c.headline}\n{c.body}\nCTA: {c.cta}" for c in copies
            )
            zf.writestr("copy.txt", copy_txt or "No copy generated.")
            for img in images:
                if img.meta and img.meta.get("storage_key") and storage.exists(img.meta["storage_key"]):
                    zf.writestr(f"images/{img.category}/{img.id}.png", storage.read_bytes(img.meta["storage_key"]))
            for v in videos:
                vk = (v.meta or {}).get("video_key")
                if vk and storage.exists(vk):
                    zf.writestr(f"videos/{v.id}.mp4", storage.read_bytes(vk))
                zf.writestr(f"videos/{v.id}-script.txt", v.script or "")
        data = buf.getvalue()
        key = f"{base_key}/campaign-{abs(hash(label)) % 100000}.zip"

    url = storage.save_bytes(key, data)
    export = Export(
        product_id=pid,
        kind=req.kind,
        label=label,
        url=url,
        size_bytes=len(data),
        meta={**meta, "storage_key": key},
    )
    db.add(export)
    await db.flush()
    await analytics_service.record_event(
        db, "export_created",
        brand_id=(product.brand_id if product else None),
        product_id=pid,
        meta={"kind": req.kind, "size": len(data)},
    )
    await db.refresh(export)
    return export


async def list_exports(db: AsyncSession, product_id: str | None = None) -> list[Export]:
    stmt = select(Export).order_by(Export.created_at.desc())
    if product_id:
        stmt = stmt.where(Export.product_id == product_id)
    rows = await db.execute(stmt)
    return list(rows.scalars().all())
