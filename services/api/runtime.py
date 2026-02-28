from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI

from packages.config.bootstrap import BootstrapState
from packages.database.session import Database
from services.api.realtime import WebSocketHub
from services.worker.checkpoint import CheckpointStore
from services.worker.queue_manager import JobQueueManager


@dataclass(slots=True)
class ApiRuntime:
    bootstrap: BootstrapState
    database: Database
    queue_manager: JobQueueManager
    checkpoint_store: CheckpointStore
    ws_hub: WebSocketHub


def get_runtime(app: FastAPI) -> ApiRuntime:
    runtime = getattr(app.state, "runtime", None)
    if runtime is None:
        raise RuntimeError("API runtime is not initialized")
    return runtime
