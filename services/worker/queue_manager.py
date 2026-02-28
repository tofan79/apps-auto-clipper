from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass, field
from time import time
from typing import Awaitable, Callable

from packages.config.logging_setup import get_logger


JobProcessor = Callable[[str, "JobQueueManager"], Awaitable[None]]


@dataclass(slots=True)
class QueueSnapshot:
    pending: list[str] = field(default_factory=list)
    running: list[str] = field(default_factory=list)
    canceled: list[str] = field(default_factory=list)


class JobQueueManager:
    """In-process async queue with cancel/reorder primitives."""

    def __init__(self, *, max_concurrent: int = 1, processor: JobProcessor | None = None) -> None:
        self._max_concurrent = max(1, max_concurrent)
        self._processor = processor
        self._pending: deque[str] = deque()
        self._running: set[str] = set()
        self._canceled: set[str] = set()
        self._lock = asyncio.Lock()
        self._workers: list[asyncio.Task[None]] = []
        self._stop_event = asyncio.Event()
        self._logger = get_logger("services.worker.queue_manager")

    def set_processor(self, processor: JobProcessor) -> None:
        self._processor = processor

    async def start(self) -> None:
        if self._workers:
            return
        self._stop_event.clear()
        for index in range(self._max_concurrent):
            task = asyncio.create_task(self._worker_loop(index), name=f"job-queue-worker-{index}")
            self._workers.append(task)

    async def stop(self) -> None:
        if not self._workers:
            return
        self._stop_event.set()
        for task in self._workers:
            task.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def enqueue(self, job_id: str) -> bool:
        async with self._lock:
            if job_id in self._running or job_id in self._pending:
                return False
            self._pending.append(job_id)
            self._logger.info("Enqueued job=%s pending=%d", job_id, len(self._pending))
            return True

    async def cancel(self, job_id: str) -> bool:
        async with self._lock:
            if job_id in self._pending:
                self._pending = deque(item for item in self._pending if item != job_id)
                self._logger.info("Canceled pending job=%s", job_id)
                return True
            if job_id in self._running:
                self._canceled.add(job_id)
                self._logger.info("Marked running job=%s for cancellation", job_id)
                return True
            return False

    async def reorder(self, job_id: str, new_index: int) -> bool:
        async with self._lock:
            if job_id not in self._pending:
                return False
            pending_list = [item for item in self._pending if item != job_id]
            bounded_index = max(0, min(new_index, len(pending_list)))
            pending_list.insert(bounded_index, job_id)
            self._pending = deque(pending_list)
            self._logger.info("Reordered job=%s to index=%d", job_id, bounded_index)
            return True

    async def snapshot(self) -> QueueSnapshot:
        async with self._lock:
            return QueueSnapshot(
                pending=list(self._pending),
                running=sorted(self._running),
                canceled=sorted(self._canceled),
            )

    async def is_cancel_requested(self, job_id: str) -> bool:
        async with self._lock:
            return job_id in self._canceled

    async def _dequeue(self) -> str | None:
        async with self._lock:
            if not self._pending:
                return None
            job_id = self._pending.popleft()
            self._running.add(job_id)
            return job_id

    async def _mark_done(self, job_id: str) -> None:
        async with self._lock:
            self._running.discard(job_id)
            self._canceled.discard(job_id)

    async def _worker_loop(self, worker_index: int) -> None:
        while not self._stop_event.is_set():
            job_id = await self._dequeue()
            if job_id is None:
                await asyncio.sleep(0.2)
                continue

            started_at = time()
            try:
                if self._processor is None:
                    self._logger.warning("No processor registered for job=%s", job_id)
                else:
                    await self._processor(job_id, self)
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._logger.exception(
                    "Queue worker failed | worker=%d | job=%s | error=%s",
                    worker_index,
                    job_id,
                    exc,
                )
            finally:
                elapsed = time() - started_at
                await self._mark_done(job_id)
                self._logger.info(
                    "Job finished | worker=%d | job=%s | elapsed=%.2fs",
                    worker_index,
                    job_id,
                    elapsed,
                )
