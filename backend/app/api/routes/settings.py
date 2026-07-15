"""Settings + system info endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.settings import SettingsRead, SettingsUpdate, SystemInfo
from app.services import settings_service

router = APIRouter()


@router.get("", response_model=SettingsRead)
async def get_settings(db: AsyncSession = Depends(get_db)):
    return await settings_service.get_settings(db)


@router.patch("", response_model=SettingsRead)
async def update_settings(payload: SettingsUpdate, db: AsyncSession = Depends(get_db)):
    return await settings_service.update_settings(db, payload)


@router.get("/system", response_model=SystemInfo)
async def system_info():
    return settings_service.system_info()
