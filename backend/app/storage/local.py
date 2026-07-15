"""Local filesystem storage backend.

Keeps a clean interface (`save_bytes` / `save_text` / `url_for` / `delete`) so a
cloud backend can implement the same shape later. Files are written under
``settings.storage_dir`` and served publicly at ``settings.storage_public_url``.
"""
from __future__ import annotations

import os
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class LocalStorage:
    def __init__(self, base_dir: str | None = None, public_url: str | None = None):
        self.base_dir = Path(base_dir or settings.storage_dir).resolve()
        self.public_url = (public_url or settings.storage_public_url).rstrip("/")
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _resolve(self, key: str) -> Path:
        # Prevent path traversal — the key must stay inside base_dir.
        key = key.lstrip("/")
        target = (self.base_dir / key).resolve()
        if not str(target).startswith(str(self.base_dir)):
            raise ValueError(f"Illegal storage key: {key!r}")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def save_bytes(self, key: str, data: bytes) -> str:
        path = self._resolve(key)
        path.write_bytes(data)
        logger.info("stored %d bytes -> %s", len(data), key)
        return self.url_for(key)

    def save_text(self, key: str, text: str) -> str:
        return self.save_bytes(key, text.encode("utf-8"))

    def read_bytes(self, key: str) -> bytes:
        return self._resolve(key).read_bytes()

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists()

    def delete(self, key: str) -> None:
        path = self._resolve(key)
        if path.exists():
            os.remove(path)

    def url_for(self, key: str) -> str:
        return f"{self.public_url}/{key.lstrip('/')}"

    def local_path(self, key: str) -> Path:
        return self._resolve(key)
