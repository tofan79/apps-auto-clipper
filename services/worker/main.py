from __future__ import annotations
# pylint: disable=wrong-import-position
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from packages.config.bootstrap import init_service_runtime
from packages.config.logging_setup import get_logger
from packages.config.memory_guard import MemoryGuard
from services.worker.checkpoint import CheckpointStore
from services.worker.queue_manager import JobQueueManager


def main() -> None:
    state = init_service_runtime("worker")
    logger = get_logger("services.worker.main")
    memory_guard = MemoryGuard(limit_gb=state.profile.ram_limit_gb)
    memory_guard.check("worker-startup")
    checkpoint_store = CheckpointStore.from_runtime()
    queue_manager = JobQueueManager(max_concurrent=state.config.get().MAX_CONCURRENT_JOBS)
    logger.info(
        "Worker bootstrap complete. Profile=%s checkpoint_dir=%s queue_concurrency=%d",
        state.profile.name,
        checkpoint_store.root_dir,
        state.config.get().MAX_CONCURRENT_JOBS,
    )
    _ = queue_manager


if __name__ == "__main__":
    main()
