from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from packages.database import crud
from services.api.runtime import get_runtime


router = APIRouter(prefix="/ws", tags=["ws"])


@router.websocket("/{job_id}")
async def job_progress_socket(websocket: WebSocket, job_id: str) -> None:
    runtime = get_runtime(websocket.app)
    hub = runtime.ws_hub

    await hub.connect(job_id, websocket)
    try:
        async with runtime.database.session() as session:
            job = await crud.get_job(session, job_id)
        if job is not None:
            await websocket.send_json(
                {
                    "job_id": job.id,
                    "status": job.status,
                    "progress_pct": job.progress_pct,
                    "current_stage": job.current_stage,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        while True:
            try:
                await asyncio.wait_for(websocket.receive_text(), timeout=30)
            except asyncio.TimeoutError:
                await websocket.send_json(
                    {
                        "job_id": job_id,
                        "status": "heartbeat",
                        "progress_pct": 0,
                        "current_stage": "heartbeat",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )
    except WebSocketDisconnect:
        await hub.disconnect(job_id, websocket)
    except Exception:
        await hub.disconnect(job_id, websocket)
