"""Settings + scraper schemas."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.schemas.common import TimestampedRead


class SettingsUpdate(BaseModel):
    theme: str | None = None
    language: str | None = None
    ai_model: str | None = None
    storage_backend: str | None = None
    generation_prefs: dict[str, Any] | None = None


class SettingsRead(TimestampedRead):
    theme: str
    language: str
    ai_model: str
    storage_backend: str
    generation_prefs: dict[str, Any] = {}
    meta: dict[str, Any] = {}


class SystemInfo(BaseModel):
    app_name: str
    version: str
    environment: str
    storage_backend: str
    # Text (OpenAI GPT)
    text_provider: str = "openai"
    text_model: str = "gpt-4o"
    text_mode: str = "mock"  # live | mock
    # Image (Google Imagen)
    image_provider: str = "google-imagen"
    image_mode: str = "mock"  # live | mock (template fallback)
    # Video (Google Veo — includes voiceover + music)
    video_provider: str = "google-veo"
    video_mode: str = "mock"  # live | mock (storyboard fallback)
    # Back-compat aliases (mirror the text provider)
    ai_mode: str = "mock"
    ai_model: str = "gpt-4o"


class ScrapeRequest(BaseModel):
    url: str
