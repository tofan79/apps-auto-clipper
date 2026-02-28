from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket

from packages.config.logging_setup import get_logger


class WebSocketHub:
    """Publish progress updates to websocket clients grouped by job id."""

    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()
        self._logger = get_logger("services.api.realtime")

    async def connect(self, job_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._channels[job_id].add(websocket)
            count = len(self._channels[job_id])
        self._logger.info("WebSocket connected | job=%s | clients=%d", job_id, count)

    async def disconnect(self, job_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            channel = self._channels.get(job_id)
            if channel is None:
                return
            channel.discard(websocket)
            count = len(channel)
            if not channel:
                self._channels.pop(job_id, None)
        self._logger.info("WebSocket disconnected | job=%s | clients=%d", job_id, count)

    async def publish(self, job_id: str, payload: dict[str, Any]) -> None:
        async with self._lock:
            targets = list(self._channels.get(job_id, set()))
        if not targets:
            return

        stale: list[WebSocket] = []
        for ws in targets:
            try:
                await ws.send_json(payload)
            except Exception:
                stale.append(ws)

        if stale:
            async with self._lock:
                channel = self._channels.get(job_id)
                if channel is None:
                    return
                for ws in stale:
                    channel.discard(ws)
                if not channel:
                    self._channels.pop(job_id, None)
