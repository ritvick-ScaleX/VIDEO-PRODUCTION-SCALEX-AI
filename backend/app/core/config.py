"""Application configuration.

All settings load from the environment (12-factor). Nothing is required to boot —
defaults produce a working local instance, and missing provider keys put each AI
layer into deterministic mock mode.

AI providers:
  • Text  (copy, analysis, UGC, scoring, storyboards) -> OpenAI GPT   [OPENAI_API_KEY]
  • Image (ad creatives)                              -> Google Imagen [GOOGLE_API_KEY]
  • Video (with native voiceover + music)             -> Google Veo    [GOOGLE_API_KEY]
"""
from __future__ import annotations

from functools import lru_cache
from typing import Annotated, Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # ---- App ----
    app_name: str = "ScaleX AI"
    environment: str = Field(default="development")
    debug: bool = True
    api_prefix: str = "/api/v1"

    # ---- Database ----
    database_url: str = Field(
        default="postgresql+asyncpg://auralis:auralis@localhost:5432/auralis"
    )
    run_migrations_on_start: bool = Field(default=True)

    # ---- Redis / Celery ----
    redis_url: str = Field(default="redis://localhost:6379/0")

    # ---- CORS ----
    # NoDecode + the validator below let CORS_ORIGINS be a plain comma-separated
    # string ("https://a.com,https://b.com") — not just JSON — in any environment.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost",
            "http://127.0.0.1:3000",
        ]
    )

    # ---- Text AI: OpenAI (GPT) ----
    openai_api_key: str = Field(default="")
    openai_model: str = Field(default="gpt-4o")
    ai_max_tokens: int = Field(default=8000)

    # ---- Image AI: Google ----
    google_api_key: str = Field(default="")
    # Nano Banana — edits the scraped product photo into pro shots (keeps the product).
    nano_banana_model: str = Field(default="gemini-2.5-flash-image")
    # Imagen — text-to-image fallback when there's no reference product photo.
    imagen_model: str = Field(default="imagen-4.0-generate-001")
    # Veo — realistic model-showcase video (person + voiceover + music).
    veo_model: str = Field(default="veo-3.1-fast-generate-preview")
    veo_timeout_seconds: int = Field(default=240)
    # Number of angle/shot clips to generate and stitch into one ad (1 = single shot).
    # Only used when there are no storyboard frames; otherwise one shot per frame.
    veo_shots: int = Field(default=3)
    # Max Veo clips generated at once. Firing every shot concurrently trips Veo's
    # per-minute rate limit and drops clips (the reel loses frames); a low cap spreads
    # them out so each one lands without burning quota on retries.
    veo_concurrency: int = Field(default=2)
    # Output resolution for realism ("720p" | "1080p"). Higher = crisper but pricier.
    veo_resolution: str = Field(default="1080p")
    # Presenter + spoken language for the video model.
    veo_presenter: str = Field(default="a friendly Indian model")
    veo_language: str = Field(default="Hindi-English (Hinglish)")
    # ONE fixed voice used across every scene (so scenes don't get different voices).
    veo_voice: str = Field(
        default=(
            "a warm, natural female Indian voice in her mid-20s, friendly and clear, "
            "conversational Hinglish delivery"
        )
    )
    # Default real-world setting bias — authentic Indian homes/locations.
    veo_setting_bias: str = Field(
        default=(
            "an authentic, real Indian home / everyday Indian setting (natural, lived-in, "
            "not a generic or artificial AI-looking backdrop)"
        )
    )

    # ---- Extra video models (multi-model variants alongside Veo) ----
    # OFF for now: Google Veo is the sole video engine until a provider that
    # exposes multiple video models from ONE API is wired up. Flip to true (and
    # point the provider config below at it) to bring the tagged variants back —
    # no code change needed.
    video_variants_enabled: bool = Field(default=False)

    # ---- Higgsfield (dormant multi-model provider; gated by the flag above) ----
    higgsfield_api_key: str = Field(default="")   # KEY_ID
    higgsfield_secret: str = Field(default="")    # KEY_SECRET
    higgsfield_base_url: str = Field(default="https://platform.higgsfield.ai")
    higgsfield_timeout_seconds: int = Field(default=360)
    # Extra models to render alongside Veo. label = UI tag; endpoint/model = Higgsfield API.
    # Editable via HIGGSFIELD_MODELS (JSON) without a code change if the catalog shifts.
    # Defaults = the video models this Higgsfield account actually exposes (DoP tiers).
    # Seedance/Kling/Gemini are NOT in the account catalogue; enable them on the
    # Higgsfield plan, then override HIGGSFIELD_MODELS (JSON) — no code change needed.
    higgsfield_models: list[dict[str, Any]] = Field(
        default_factory=lambda: [
            {"label": "DoP Turbo", "endpoint": "/v1/image2video/dop", "model": "dop-turbo", "params": {}},
            {"label": "DoP Standard", "endpoint": "/v1/image2video/dop", "model": "dop-preview", "params": {}},
            {"label": "DoP Lite", "endpoint": "/v1/image2video/dop", "model": "dop-lite", "params": {}},
        ]
    )

    # ---- Ideas ----
    ideas_count: int = Field(default=4)

    # ---- Video engine ----
    # "veo"    = realistic Veo 3.1 image-to-video (a model showcases the product)
    # "heygen" = talking-head avatar presenter
    # The other engine is used as a fallback automatically.
    video_engine: str = Field(default="veo")

    # ---- Video AI: HeyGen (talking-head avatar showcasing the product) ----
    heygen_api_key: str = Field(default="")
    # Pin a specific avatar/voice, or leave blank to auto-select + rotate.
    heygen_avatar_id: str = Field(default="")
    heygen_voice_id: str = Field(default="")
    # Preferred region/accent for auto-selection (avatar look + voice accent).
    heygen_region: str = Field(default="india")
    # Rotate to a different avatar on every render for variety.
    heygen_rotate_avatars: bool = Field(default=True)
    heygen_timeout_seconds: int = Field(default=300)

    # ---- Storage ----
    storage_backend: str = Field(default="local")
    storage_dir: str = Field(default="./storage_data")
    storage_public_url: str = Field(default="http://localhost:8000/static")

    @property
    def text_ai_enabled(self) -> bool:
        return bool(self.openai_api_key.strip())

    @property
    def google_ai_enabled(self) -> bool:
        return bool(self.google_api_key.strip())

    @property
    def heygen_enabled(self) -> bool:
        return bool(self.heygen_api_key.strip())

    @property
    def higgsfield_enabled(self) -> bool:
        return bool(self.higgsfield_api_key.strip() and self.higgsfield_secret.strip())

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("database_url", mode="before")
    @classmethod
    def _async_db_url(cls, v):
        """Accept a plain Postgres URL (Railway/Heroku style) and make it async."""
        if isinstance(v, str):
            if v.startswith("postgres://"):
                v = "postgresql+asyncpg://" + v[len("postgres://"):]
            elif v.startswith("postgresql://"):
                v = "postgresql+asyncpg://" + v[len("postgresql://"):]
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
