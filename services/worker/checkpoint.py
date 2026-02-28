from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packages.config.app_paths import ensure_runtime_paths


@dataclass(slots=True)
class CheckpointStore:
    """Checkpoint persistence for job progress recovery."""

    root_dir: Path

    @classmethod
    def from_runtime(cls) -> "CheckpointStore":
        runtime = ensure_runtime_paths()
        root_dir = runtime.downloads_dir
        root_dir.mkdir(parents=True, exist_ok=True)
        return cls(root_dir=root_dir)

    def path_for(self, job_id: str) -> Path:
        safe_id = "".join(ch for ch in job_id if ch.isalnum() or ch in ("-", "_"))
        return self.root_dir / safe_id / "checkpoint.json"

    def save(self, job_id: str, payload: dict[str, Any]) -> Path:
        path = self.path_for(job_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = path.with_suffix(".tmp")
        temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        temp_path.replace(path)
        return path

    def load(self, job_id: str) -> dict[str, Any] | None:
        path = self.path_for(job_id)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None

    def delete(self, job_id: str) -> None:
        path = self.path_for(job_id)
        path.unlink(missing_ok=True)
