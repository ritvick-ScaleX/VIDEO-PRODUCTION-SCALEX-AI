"""Project CRUD endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.schemas.common import MessageResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetail,
    ProjectRead,
    ProjectUpdate,
)
from app.services import project_service

router = APIRouter()


@router.get("", response_model=list[ProjectDetail])
async def list_projects(db: AsyncSession = Depends(get_db)):
    return await project_service.list_projects(db)


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)):
    return await project_service.create_project(db, payload)


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    return await project_service.get_project(db, project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: str, payload: ProjectUpdate, db: AsyncSession = Depends(get_db)
):
    return await project_service.update_project(db, project_id, payload)


@router.delete("/{project_id}", response_model=MessageResponse)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    await project_service.delete_project(db, project_id)
    return MessageResponse(message="Project deleted")
