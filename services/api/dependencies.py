from __future__ import annotations

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from services.api.realtime import WebSocketHub
from services.api.runtime import ApiRuntime, get_runtime
from services.worker.checkpoint import CheckpointStore
from services.worker.queue_manager import JobQueueManager


def get_api_runtime(request: Request) -> ApiRuntime:
    return get_runtime(request.app)


def get_queue_manager(request: Request) -> JobQueueManager:
    return get_runtime(request.app).queue_manager


def get_checkpoint_store(request: Request) -> CheckpointStore:
    return get_runtime(request.app).checkpoint_store


def get_ws_hub(request: Request) -> WebSocketHub:
    return get_runtime(request.app).ws_hub


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    runtime = get_runtime(request.app)
    async with runtime.database.session() as session:
        yield session
