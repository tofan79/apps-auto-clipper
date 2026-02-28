from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database import crud
from services.api.dependencies import get_db_session
from services.api.schemas import ClipPreviewResponse, ClipResponse


router = APIRouter(prefix="/clips", tags=["clips"])


@router.get("/{job_id}", response_model=list[ClipResponse])
async def get_clips_for_job(job_id: str, session: AsyncSession = Depends(get_db_session)) -> list[ClipResponse]:
    job = await crud.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    clips = await crud.get_clips_by_job(session, job_id)
    return [ClipResponse.model_validate(clip) for clip in clips]


@router.get("/{clip_id}/preview", response_model=ClipPreviewResponse)
async def get_clip_preview(clip_id: str, session: AsyncSession = Depends(get_db_session)) -> ClipPreviewResponse:
    clip = await crud.get_clip(session, clip_id)
    if clip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Clip not found")

    try:
        metadata = json.loads(clip.metadata_json) if clip.metadata_json else {}
    except json.JSONDecodeError:
        metadata = {}

    return ClipPreviewResponse(
        clip_id=clip.id,
        file_path=clip.file_path,
        thumbnail_path=clip.thumbnail_path,
        metadata=metadata,
    )
