"""Async engine, session factory, and FastAPI dependency."""
from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency yielding a scoped async session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Lightweight in-place column additions — create_all() never ALTERs existing
# tables, so new columns land here. Each runs in its own transaction and is a
# no-op if the column already exists. (Alembic replaces this eventually.)
_COLUMN_PATCHES: list[str] = [
    "ALTER TABLE products ADD COLUMN ingredients JSON DEFAULT '[]'",
    "ALTER TABLE products ADD COLUMN selected_images JSON DEFAULT '[]'",
    "ALTER TABLE ideas ADD COLUMN kind VARCHAR(12) DEFAULT 'video'",
    "ALTER TABLE generated_images ADD COLUMN review_status VARCHAR(12) DEFAULT 'pending'",
    "ALTER TABLE generated_images ADD COLUMN review_comment TEXT",
    # Backfill NULLs so list/str fields validate cleanly.
    "UPDATE products SET ingredients = '[]' WHERE ingredients IS NULL",
    "UPDATE products SET selected_images = '[]' WHERE selected_images IS NULL",
    "UPDATE ideas SET kind = 'video' WHERE kind IS NULL",
    "UPDATE generated_images SET review_status = 'pending' WHERE review_status IS NULL",
]


async def init_db() -> None:
    """Create all tables (MVP convenience; Alembic handles real migrations)."""
    # Import models so they register on the metadata before create_all.
    from sqlalchemy import text

    from app import models  # noqa: F401
    from app.database.base import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    for stmt in _COLUMN_PATCHES:
        try:
            async with engine.begin() as conn:
                await conn.execute(text(stmt))
        except Exception:
            pass  # column already exists — expected on every boot after the first
