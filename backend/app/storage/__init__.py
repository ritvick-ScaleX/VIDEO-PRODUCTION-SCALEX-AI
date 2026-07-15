"""Pluggable asset storage.

`LocalStorage` writes to disk for the MVP. The `Storage` protocol is the seam
that lets an `S3Storage` / `R2Storage` drop in later without touching services.
"""
from __future__ import annotations

from app.core.config import settings
from app.storage.local import LocalStorage

_backends = {
    "local": LocalStorage,
}


def get_storage():
    backend = _backends.get(settings.storage_backend, LocalStorage)
    return backend()


storage = get_storage()

__all__ = ["storage", "get_storage", "LocalStorage"]
