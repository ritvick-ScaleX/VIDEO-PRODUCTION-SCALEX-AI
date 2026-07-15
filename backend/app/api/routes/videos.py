"""Video endpoints — script draft, edit/reprompt, frames, render (prefix /products)."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.generation import (
    RepromptRequest,
    SaveToggle,
    VideoGenerateRequest,
    VideoRead,
    VideoUpdate,
)
from app.services import video_service

router = APIRouter()


@router.get("/{product_id}/videos", response_model=list[VideoRead])
async def list_videos(product_id: str, db: AsyncSession = Depends(get_db)):
    return await video_service.list_for_product(db, product_id)


@router.post("/{product_id}/videos", response_model=VideoRead)
async def create_script(product_id: str, payload: VideoGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Draft a Hinglish script + storyboard (from the selected idea if given)."""
    return await video_service.create_script(db, product_id, payload)


@router.patch("/{product_id}/videos/{video_id}", response_model=VideoRead)
async def update_video(product_id: str, video_id: str, payload: VideoUpdate, db: AsyncSession = Depends(get_db)):
    return await video_service.update(db, video_id, payload)


@router.post("/{product_id}/videos/{video_id}/reprompt", response_model=VideoRead)
async def reprompt_video(product_id: str, video_id: str, payload: RepromptRequest, db: AsyncSession = Depends(get_db)):
    return await video_service.reprompt(db, video_id, payload.instructions)


@router.post("/{product_id}/videos/{video_id}/frames", response_model=VideoRead)
async def generate_frames(product_id: str, video_id: str, db: AsyncSession = Depends(get_db)):
    return await video_service.generate_frames(db, product_id, video_id)


@router.post("/{product_id}/videos/{video_id}/render", response_model=VideoRead)
async def render_video(product_id: str, video_id: str, db: AsyncSession = Depends(get_db)):
    """Kick off the render and return immediately (status='rendering'); the client polls
    the video list until it becomes 'ready'/'error'. The Veo work is minutes long and
    would otherwise time out behind the edge proxy."""
    video = await video_service.begin_render(db, product_id, video_id)
    await db.commit()  # persist 'rendering' before the background task reads it
    asyncio.create_task(video_service.render_background(product_id, video_id))
    return video


@router.patch("/{product_id}/videos/{video_id}/save", response_model=VideoRead)
async def save_video(product_id: str, video_id: str, payload: SaveToggle, db: AsyncSession = Depends(get_db)):
    obj = await video_service.set_saved(db, video_id, payload.is_saved)
    if not obj:
        raise HTTPException(status_code=404, detail="Video not found")
    return obj


@router.delete("/{product_id}/videos/{video_id}", response_model=MessageResponse)
async def delete_video(product_id: str, video_id: str, db: AsyncSession = Depends(get_db)):
    await video_service.delete(db, video_id)
    return MessageResponse(message="Deleted")
