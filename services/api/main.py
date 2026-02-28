from __future__ import annotations
# pylint: disable=wrong-import-position
# ruff: noqa: E402

import asyncio
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
try:
    import uvicorn
except ModuleNotFoundError:
    uvicorn = None  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.logging_setup import get_logger
from packages.database import crud
from packages.database.session import Database
from services.api.realtime import WebSocketHub
from services.api.routers.clips import router as clips_router
from services.api.routers.jobs import router as jobs_router
from services.api.routers.settings import router as settings_router
from services.api.routers.ws import router as ws_router
from services.api.runtime import ApiRuntime
from services.api.schemas import HealthResponse
from services.worker.checkpoint import CheckpointStore
from services.worker.queue_manager import JobQueueManager


logger = get_logger("services.api.main")


async def _publish_progress(
    runtime: ApiRuntime,
    *,
    job_id: str,
    status: str,
    progress_pct: int,
    current_stage: str | None,
    message: str | None = None,
) -> None:
    await runtime.ws_hub.publish(
        job_id,
        {
            "job_id": job_id,
            "status": status,
            "progress_pct": progress_pct,
            "current_stage": current_stage,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )


async def _mark_job_canceled(runtime: ApiRuntime, job_id: str, progress_pct: int) -> None:
    runtime.checkpoint_store.delete(job_id)
    async with runtime.database.session() as session:
        await crud.update_job_status(
            session,
            job_id=job_id,
            status="canceled",
            current_stage="canceled",
            progress_pct=progress_pct,
            error_msg="Canceled by user",
        )
    await _publish_progress(
        runtime,
        job_id=job_id,
        status="canceled",
        progress_pct=progress_pct,
        current_stage="canceled",
        message="Job canceled",
    )


async def _process_job(runtime: ApiRuntime, job_id: str, queue_manager: JobQueueManager) -> None:
    checkpoint_path = runtime.checkpoint_store.path_for(job_id)
    checkpoint = runtime.checkpoint_store.load(job_id) or {}
    last_progress = int(checkpoint.get("progress_pct", 0))
    checkpoint_stage = str(checkpoint.get("current_stage", "")).strip()

    try:
        async with runtime.database.session() as session:
            job = await crud.update_job_status(
                session,
                job_id=job_id,
                status="running",
                current_stage="started",
                progress_pct=max(5, last_progress),
                checkpoint_path=str(checkpoint_path),
            )
            if job is None:
                return

        await _publish_progress(
            runtime,
            job_id=job_id,
            status="running",
            progress_pct=max(5, last_progress),
            current_stage="started",
            message="Job started",
        )

        stages: list[tuple[str, int]] = [
            ("ingest", 20),
            ("transcribe", 55),
            ("render", 100),
        ]
        stage_names = [name for name, _ in stages]
        start_index = 0
        if checkpoint_stage in stage_names:
            stage_index = stage_names.index(checkpoint_stage)
            stage_progress = stages[stage_index][1]
            start_index = stage_index + 1 if last_progress >= stage_progress else stage_index
        if start_index >= len(stages):
            start_index = len(stages) - 1

        if start_index > 0:
            await _publish_progress(
                runtime,
                job_id=job_id,
                status="running",
                progress_pct=last_progress,
                current_stage=checkpoint_stage or "resume",
                message="Resuming from checkpoint",
            )

        for stage_name, progress_pct in stages[start_index:]:
            if await queue_manager.is_cancel_requested(job_id):
                await _mark_job_canceled(runtime, job_id, last_progress)
                return

            payload = {
                "job_id": job_id,
                "status": "running",
                "current_stage": stage_name,
                "progress_pct": progress_pct,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            runtime.checkpoint_store.save(job_id, payload)

            async with runtime.database.session() as session:
                await crud.update_job_status(
                    session,
                    job_id=job_id,
                    status="running",
                    current_stage=stage_name,
                    progress_pct=progress_pct,
                    checkpoint_path=str(checkpoint_path),
                )

            await _publish_progress(
                runtime,
                job_id=job_id,
                status="running",
                progress_pct=progress_pct,
                current_stage=stage_name,
            )
            last_progress = progress_pct
            await asyncio.sleep(0.25)

        async with runtime.database.session() as session:
            clips = await crud.get_clips_by_job(session, job_id)
            if not clips:
                await crud.create_clip(
                    session,
                    clip_id=uuid.uuid4().hex,
                    job_id=job_id,
                    file_path=str(runtime.bootstrap.paths.clips_dir / f"{job_id}_clip_001.mp4"),
                    thumbnail_path=str(runtime.bootstrap.paths.clips_dir / f"{job_id}_clip_001.jpg"),
                    mode="portrait",
                    viral_score=0,
                    duration_sec=0,
                    metadata={"generated_by": "stage2_stub"},
                )
            await crud.update_job_status(
                session,
                job_id=job_id,
                status="done",
                current_stage="completed",
                progress_pct=100,
                error_msg=None,
            )

        runtime.checkpoint_store.delete(job_id)
        await _publish_progress(
            runtime,
            job_id=job_id,
            status="done",
            progress_pct=100,
            current_stage="completed",
            message="Job completed",
        )
    except Exception as exc:
        async with runtime.database.session() as session:
            await crud.update_job_status(
                session,
                job_id=job_id,
                status="failed",
                current_stage="failed",
                progress_pct=last_progress,
                error_msg=str(exc),
                checkpoint_path=str(checkpoint_path),
            )
        await _publish_progress(
            runtime,
            job_id=job_id,
            status="failed",
            progress_pct=last_progress,
            current_stage="failed",
            message=str(exc),
        )
        logger.exception("Job processing failed | job=%s | error=%s", job_id, exc)


async def _recover_jobs(runtime: ApiRuntime) -> int:
    async with runtime.database.session() as session:
        resumable = await crud.list_jobs_by_status(session, {"pending", "queued", "running"})
        job_ids = [job.id for job in resumable]
        for job in resumable:
            await crud.update_job_status(
                session,
                job_id=job.id,
                status="queued",
                current_stage=job.current_stage or "queued",
                progress_pct=job.progress_pct,
                checkpoint_path=str(runtime.checkpoint_store.path_for(job.id)),
            )
    recovered = 0
    for job_id in job_ids:
        accepted = await runtime.queue_manager.enqueue(job_id)
        if accepted:
            recovered += 1
    return recovered


@asynccontextmanager
async def lifespan(app: FastAPI):
    bootstrap = init_service_runtime("api")
    database = Database.create()
    await database.init_models()

    ws_hub = WebSocketHub()
    checkpoint_store = CheckpointStore.from_runtime()
    max_concurrent = int(bootstrap.config.get().MAX_CONCURRENT_JOBS)
    queue_manager = JobQueueManager(max_concurrent=max_concurrent)

    runtime = ApiRuntime(
        bootstrap=bootstrap,
        database=database,
        queue_manager=queue_manager,
        checkpoint_store=checkpoint_store,
        ws_hub=ws_hub,
    )
    app.state.runtime = runtime

    async def processor(job_id: str, manager: JobQueueManager) -> None:
        await _process_job(runtime, job_id, manager)

    queue_manager.set_processor(processor)
    await queue_manager.start()
    recovered_count = await _recover_jobs(runtime)
    logger.info("API started | host=127.0.0.1 | port=8000")
    if recovered_count > 0:
        logger.info("Recovered %d resumable jobs into queue", recovered_count)
    try:
        yield
    finally:
        await queue_manager.stop()
        await database.close()
        logger.info("API stopped")


app = FastAPI(
    title="AutoClipper API",
    version="0.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(clips_router)
app.include_router(settings_router)
app.include_router(ws_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", service="api")


def main() -> None:
    if uvicorn is None:
        raise RuntimeError("uvicorn is required to run API service. Install services/api/requirements.txt first.")
    uvicorn.run("services.api.main:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
