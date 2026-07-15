"""ORM models. Importing this package registers every table on the metadata.

Hierarchy: Brand -> Product -> (Images, Ideas, Videos, Copy, Scores).
"""
from app.models.analytics import AnalyticsEvent
from app.models.brand import Brand
from app.models.export import Export
from app.models.generation import (
    GeneratedCopy,
    GeneratedImage,
    GeneratedVideo,
    UGCScript,
)
from app.models.idea import Idea
from app.models.product import Product
from app.models.scoring import CreativeScore
from app.models.settings import AppSettings

__all__ = [
    "Brand",
    "Product",
    "Idea",
    "GeneratedCopy",
    "GeneratedImage",
    "GeneratedVideo",
    "UGCScript",
    "CreativeScore",
    "Export",
    "AnalyticsEvent",
    "AppSettings",
]
