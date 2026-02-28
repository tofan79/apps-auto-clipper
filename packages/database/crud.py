from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.database.models import Clip, Job, Setting


VALID_SOURCE_TYPES = {"youtube", "local"}
VALID_JOB_STATUSES = {"pending", "queued", "running", "done", "failed", "canceled"}
VALID_CLIP_MODES = {"portrait", "landscape"}


async def create_job(
    session: AsyncSession,
    *,
    job_id: str,
    source_url: str,
    source_type: str,
    user_id: str | None = None,
    checkpoint_path: str | None = None,
) -> Job:
    """Create a new job row."""
    if source_type not in VALID_SOURCE_TYPES:
        raise ValueError(f"Invalid source_type: {source_type}")

    job = Job(
        id=job_id,
        user_id=user_id,
        source_url=source_url,
        source_type=source_type,
        status="pending",
        progress_pct=0,
        current_stage="created",
        checkpoint_path=checkpoint_path,
    )
    session.add(job)
    await session.flush()
    await session.refresh(job)
    return job


async def list_jobs(session: AsyncSession, *, limit: int = 100, offset: int = 0) -> list[Job]:
    """Return jobs sorted by latest update."""
    result = await session.execute(
        select(Job).order_by(Job.updated_at.desc()).limit(limit).offset(offset)
    )
    return list(result.scalars().all())


async def list_jobs_by_status(
    session: AsyncSession,
    statuses: set[str],
    *,
    limit: int = 200,
) -> list[Job]:
    """Return jobs filtered by a set of statuses."""
    if not statuses:
        return []
    result = await session.execute(
        select(Job)
        .where(Job.status.in_(statuses))
        .order_by(Job.updated_at.asc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_job(session: AsyncSession, job_id: str) -> Job | None:
    """Get job by id."""
    result = await session.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def update_job_status(
    session: AsyncSession,
    *,
    job_id: str,
    status: str,
    current_stage: str | None = None,
    progress_pct: int | None = None,
    error_msg: str | None = None,
    checkpoint_path: str | None = None,
) -> Job | None:
    """Update job status/progress fields."""
    if status not in VALID_JOB_STATUSES:
        raise ValueError(f"Invalid status: {status}")

    job = await get_job(session, job_id)
    if job is None:
        return None

    job.status = status
    if current_stage is not None:
        job.current_stage = current_stage
    if progress_pct is not None:
        bounded_pct = max(0, min(100, progress_pct))
        job.progress_pct = bounded_pct
    if error_msg is not None:
        job.error_msg = error_msg
    if checkpoint_path is not None:
        job.checkpoint_path = checkpoint_path
    await session.flush()
    await session.refresh(job)
    return job


async def create_clip(
    session: AsyncSession,
    *,
    clip_id: str,
    job_id: str,
    file_path: str,
    thumbnail_path: str | None = None,
    mode: str = "portrait",
    viral_score: int = 0,
    duration_sec: int = 0,
    metadata: dict[str, Any] | None = None,
) -> Clip:
    """Create a clip row."""
    if mode not in VALID_CLIP_MODES:
        raise ValueError(f"Invalid mode: {mode}")

    clip = Clip(
        id=clip_id,
        job_id=job_id,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        mode=mode,
        viral_score=max(0, viral_score),
        duration_sec=max(0, duration_sec),
        metadata_json=json.dumps(metadata or {}, ensure_ascii=True),
    )
    session.add(clip)
    await session.flush()
    await session.refresh(clip)
    return clip


async def get_clip(session: AsyncSession, clip_id: str) -> Clip | None:
    """Get clip by id."""
    result = await session.execute(select(Clip).where(Clip.id == clip_id))
    return result.scalar_one_or_none()


async def get_clips_by_job(session: AsyncSession, job_id: str) -> list[Clip]:
    """Get all clips for a job."""
    result = await session.execute(select(Clip).where(Clip.job_id == job_id).order_by(Clip.created_at.asc()))
    return list(result.scalars().all())


async def upsert_setting(session: AsyncSession, *, key: str, value: str) -> Setting:
    """Insert or update a setting row."""
    result = await session.execute(select(Setting).where(Setting.key == key))
    existing = result.scalar_one_or_none()
    if existing is None:
        setting = Setting(key=key, value=value)
        session.add(setting)
        await session.flush()
        await session.refresh(setting)
        return setting

    existing.value = value
    await session.flush()
    await session.refresh(existing)
    return existing


async def get_settings(session: AsyncSession) -> dict[str, str]:
    """Return all settings as key/value pairs."""
    result = await session.execute(select(Setting))
    rows = result.scalars().all()
    return {item.key: item.value for item in rows}
