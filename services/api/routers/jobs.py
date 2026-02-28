from __future__ import annotations

from datetime import datetime, timezone
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database import crud
from services.api.dependencies import get_checkpoint_store, get_db_session, get_queue_manager
from services.api.schemas import (
    JobCreateRequest,
    JobQueueActionResponse,
    JobReorderRequest,
    JobResponse,
    JobStatusResponse,
)
from services.worker.checkpoint import CheckpointStore
from services.worker.queue_manager import JobQueueManager


router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    payload: JobCreateRequest,
    session: AsyncSession = Depends(get_db_session),
    queue_manager: JobQueueManager = Depends(get_queue_manager),
    checkpoint_store: CheckpointStore = Depends(get_checkpoint_store),
) -> JobResponse:
    job_id = uuid.uuid4().hex
    checkpoint_path = str(checkpoint_store.path_for(job_id))
    checkpoint_store.save(
        job_id,
        {
            "job_id": job_id,
            "status": "queued",
            "current_stage": "queued",
            "progress_pct": 0,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    await crud.create_job(
        session,
        job_id=job_id,
        source_url=payload.source_url,
        source_type=payload.source_type,
        user_id=payload.user_id,
        checkpoint_path=checkpoint_path,
    )

    accepted = await queue_manager.enqueue(job_id)
    if not accepted:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Job is already queued")

    job = await crud.update_job_status(
        session,
        job_id=job_id,
        status="queued",
        current_stage="queued",
        progress_pct=0,
        checkpoint_path=checkpoint_path,
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to queue job")

    return JobResponse.model_validate(job)


@router.get("", response_model=list[JobResponse])
async def list_jobs(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_db_session),
) -> list[JobResponse]:
    jobs = await crud.list_jobs(session, limit=limit, offset=offset)
    return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str, session: AsyncSession = Depends(get_db_session)) -> JobResponse:
    job = await crud.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobResponse.model_validate(job)


@router.get("/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str, session: AsyncSession = Depends(get_db_session)) -> JobStatusResponse:
    job = await crud.get_job(session, job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return JobStatusResponse(
        id=job.id,
        status=job.status,
        progress_pct=job.progress_pct,
        current_stage=job.current_stage,
        error_msg=job.error_msg,
    )


@router.post("/{job_id}/cancel", response_model=JobQueueActionResponse)
async def cancel_job(
    job_id: str,
    session: AsyncSession = Depends(get_db_session),
    queue_manager: JobQueueManager = Depends(get_queue_manager),
) -> JobQueueActionResponse:
    existing = await crud.get_job(session, job_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    accepted = await queue_manager.cancel(job_id)
    if accepted:
        await crud.update_job_status(
            session,
            job_id=job_id,
            status="canceled",
            current_stage="canceled",
            progress_pct=existing.progress_pct,
            error_msg="Canceled by user",
        )
    return JobQueueActionResponse(id=job_id, accepted=accepted)


@router.post("/{job_id}/reorder", response_model=JobQueueActionResponse)
async def reorder_job(
    job_id: str,
    payload: JobReorderRequest,
    session: AsyncSession = Depends(get_db_session),
    queue_manager: JobQueueManager = Depends(get_queue_manager),
) -> JobQueueActionResponse:
    existing = await crud.get_job(session, job_id)
    if existing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    accepted = await queue_manager.reorder(job_id, payload.index)
    return JobQueueActionResponse(id=job_id, accepted=accepted)
