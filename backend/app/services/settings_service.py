"""Settings service — singleton preferences + system info."""
from __future__ import annotations

from app import __version__
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings as app_settings
from app.models.settings import SINGLETON_ID, AppSettings
from app.schemas.settings import SettingsUpdate, SystemInfo
from app.services.ai import llm


async def get_settings(db: AsyncSession) -> AppSettings:
    obj = await db.get(AppSettings, SINGLETON_ID)
    if obj is None:
        obj = AppSettings(
            id=SINGLETON_ID,
            ai_model=app_settings.openai_model,
            storage_backend=app_settings.storage_backend,
            generation_prefs={
                "default_tone": "professional",
                "default_variations": 3,
                "auto_score": True,
            },
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
    return obj


async def update_settings(db: AsyncSession, data: SettingsUpdate) -> AppSettings:
    obj = await get_settings(db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.flush()
    await db.refresh(obj)
    return obj


def system_info() -> SystemInfo:
    from app.services.ai import heygen, media

    text_mode = llm.mode
    image_mode = "live" if media.images_enabled() else "mock"
    if app_settings.video_engine == "veo":
        video_mode = "live" if app_settings.google_ai_enabled else "mock"
    else:
        video_mode = "live" if heygen.enabled() else "mock"
    # Provider/model names are intentionally generic — the engine is a black box.
    return SystemInfo(
        app_name=app_settings.app_name,
        version=__version__,
        environment=app_settings.environment,
        storage_backend=app_settings.storage_backend,
        text_provider="ScaleX Engine",
        text_model="ScaleX Text",
        text_mode=text_mode,
        image_provider="ScaleX Engine",
        image_mode=image_mode,
        video_provider="ScaleX Engine",
        video_mode=video_mode,
        ai_mode=text_mode,
        ai_model="ScaleX Engine",
    )
