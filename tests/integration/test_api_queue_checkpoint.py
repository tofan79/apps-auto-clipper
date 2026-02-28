from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient

from services.api.main import app


def _wait_until(
    predicate: Callable[[], bool],
    *,
    timeout: float = 10.0,
    interval: float = 0.1,
) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return False


def _status(client: TestClient, job_id: str) -> dict[str, Any]:
    response = client.get(f"/jobs/{job_id}/status")
    assert response.status_code == 200
    return response.json()


def test_api_job_lifecycle_includes_queue_and_checkpoint(tmp_path: Path, monkeypatch) -> None:
    runtime_root = tmp_path / "runtime-api-lifecycle"
    monkeypatch.setenv("AUTOCLIPPER_APPDATA", str(runtime_root))

    with TestClient(app) as client:
        created = client.post(
            "/jobs",
            json={"source_url": "local://sample.mp4", "source_type": "local"},
        )
        assert created.status_code == 201
        payload = created.json()
        job_id = payload["id"]
        checkpoint_path = Path(payload["checkpoint_path"])

        assert f"storage/downloads/{job_id}/checkpoint.json" in checkpoint_path.as_posix()
        assert _wait_until(lambda: checkpoint_path.exists(), timeout=4.0)

        assert _wait_until(
            lambda: _status(client, job_id)["status"] == "done",
            timeout=12.0,
        )
        final_status = _status(client, job_id)
        assert final_status["progress_pct"] == 100
        assert not checkpoint_path.exists()

        clips = client.get(f"/clips/{job_id}")
        assert clips.status_code == 200
        assert len(clips.json()) >= 1


def test_queue_runs_jobs_sequentially(tmp_path: Path, monkeypatch) -> None:
    runtime_root = tmp_path / "runtime-queue-sequential"
    monkeypatch.setenv("AUTOCLIPPER_APPDATA", str(runtime_root))

    with TestClient(app) as client:
        job1 = client.post(
            "/jobs",
            json={"source_url": "local://video-a.mp4", "source_type": "local"},
        ).json()
        job2 = client.post(
            "/jobs",
            json={"source_url": "local://video-b.mp4", "source_type": "local"},
        ).json()

        job1_id = job1["id"]
        job2_id = job2["id"]

        seen_running_then_queued = False
        deadline = time.time() + 12.0
        while time.time() < deadline:
            s1 = _status(client, job1_id)["status"]
            s2 = _status(client, job2_id)["status"]
            if s1 == "running" and s2 == "queued":
                seen_running_then_queued = True
            if s1 == "done" and s2 == "done":
                break
            time.sleep(0.1)

        assert seen_running_then_queued
        assert _status(client, job1_id)["status"] == "done"
        assert _status(client, job2_id)["status"] == "done"


def test_websocket_progress_channel_available(tmp_path: Path, monkeypatch) -> None:
    runtime_root = tmp_path / "runtime-ws"
    monkeypatch.setenv("AUTOCLIPPER_APPDATA", str(runtime_root))

    with TestClient(app) as client:
        created = client.post(
            "/jobs",
            json={"source_url": "local://sample-ws.mp4", "source_type": "local"},
        )
        assert created.status_code == 201
        job_id = created.json()["id"]

        with client.websocket_connect(f"/ws/{job_id}") as websocket:
            message = websocket.receive_json()
            assert message["job_id"] == job_id
            assert "status" in message
            assert "progress_pct" in message
