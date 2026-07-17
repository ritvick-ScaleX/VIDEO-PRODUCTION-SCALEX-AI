"""Request/response schemas for the generators (product-scoped)."""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.common import TimestampedRead

# --------------------------------------------------------------------------- #
# Copy
# --------------------------------------------------------------------------- #
CopyPlatform = Literal[
    "facebook", "instagram", "google", "linkedin",
    "twitter", "landing_page", "email", "headline",
]
Tone = Literal["luxury", "professional", "friendly", "minimal"]


class CopyGenerateRequest(BaseModel):
    platform: CopyPlatform = "facebook"
    tone: Tone = "professional"
    variations: int = Field(default=3, ge=1, le=6)
    instructions: str | None = None


class CopyRead(TimestampedRead):
    product_id: str
    platform: str
    tone: str
    headline: str | None = None
    body: str | None = None
    cta: str | None = None
    variations: list[dict[str, Any]] = []
    meta: dict[str, Any] = {}
    is_saved: bool = False


# --------------------------------------------------------------------------- #
# Image
# --------------------------------------------------------------------------- #
ImageFormat = Literal[
    "square", "portrait", "landscape", "story", "carousel", "poster", "lifestyle"
]
ImageCategory = Literal["white_background", "creative", "product_shot"]


class ImageGenerateRequest(BaseModel):
    category: ImageCategory = "creative"
    format: ImageFormat = "square"
    prompt: str | None = None
    idea_id: str | None = None  # build the image from this market angle
    count: int = Field(default=1, ge=1, le=6)
    headline: str | None = None
    cta: str | None = None


class ImageReviewRequest(BaseModel):
    status: Literal["accepted", "rejected", "pending"]
    comment: str | None = None  # rejection feedback — becomes avoid-context next run


class ImageRead(TimestampedRead):
    product_id: str
    category: str
    format: str
    prompt: str | None = None
    url: str
    width: int
    height: int
    meta: dict[str, Any] = {}
    is_saved: bool = False
    review_status: str = "pending"
    review_comment: str | None = None


# --------------------------------------------------------------------------- #
# Video (idea -> script -> frames -> render)
# --------------------------------------------------------------------------- #
VideoDuration = Literal["15s", "30s", "60s", "reel", "short", "story"]


class VideoGenerateRequest(BaseModel):
    duration: VideoDuration = "reel"
    format: str = "reel"
    instructions: str | None = None
    idea_id: str | None = None  # build the script from this selected idea


class ScriptFromIdeaRequest(BaseModel):
    idea_id: str
    duration: VideoDuration = "reel"
    format: str = "reel"
    instructions: str | None = None


class RepromptRequest(BaseModel):
    instructions: str = Field(..., min_length=1)


class VideoUpdate(BaseModel):
    script: str | None = None
    voiceover: str | None = None
    status: str | None = None


class VideoRead(TimestampedRead):
    product_id: str
    idea_id: str | None = None
    duration: str
    format: str
    script: str | None = None
    storyboard: list[dict[str, Any]] = []
    voiceover: str | None = None
    captions: list[str] = []
    transitions: list[str] = []
    frame_urls: list[str] = []
    thumbnail_url: str | None = None
    video_url: str | None = None
    status: str = "draft"
    progress: int = 0
    meta: dict[str, Any] = {}
    is_saved: bool = False


# --------------------------------------------------------------------------- #
# UGC
# --------------------------------------------------------------------------- #
class UGCGenerateRequest(BaseModel):
    voice_style: str = "authentic"
    emotion: str = "excited"
    audience: str | None = None
    instructions: str | None = None


class UGCRead(TimestampedRead):
    product_id: str
    hook: str | None = None
    script: str | None = None
    camera_directions: list[str] = []
    scene_breakdown: list[dict[str, Any]] = []
    b_roll: list[str] = []
    cta: str | None = None
    voice_style: str | None = None
    emotion: str | None = None
    audience: str | None = None
    meta: dict[str, Any] = {}
    is_saved: bool = False


class SaveToggle(BaseModel):
    is_saved: bool = True
