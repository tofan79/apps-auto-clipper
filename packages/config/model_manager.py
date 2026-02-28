from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from packages.config.app_paths import ensure_runtime_paths
from packages.shared.security import sanitize_filename


DownloadCallback = Callable[[Path, Callable[[int, int], None] | None], None]
ProgressCallback = Callable[[int, int], None]


@dataclass(slots=True)
class ModelManager:
    """
    Manages local Whisper model artifacts for Stage 3.
    """

    model_root: Path

    @classmethod
    def from_runtime(cls) -> "ModelManager":
        return cls(model_root=ensure_runtime_paths().models_dir)

    def model_path(self, model_name: str) -> Path:
        safe_name = sanitize_filename(model_name, default="model")
        return self.model_root / f"{safe_name}.bin"

    def ensure_model(
        self,
        model_name: str,
        *,
        expected_sha256: str | None = None,
        downloader: DownloadCallback | None = None,
        progress: ProgressCallback | None = None,
    ) -> Path:
        """
        Ensure a model file exists and optionally matches expected hash.
        """
        self.model_root.mkdir(parents=True, exist_ok=True)
        target = self.model_path(model_name)

        if target.exists() and self._is_valid(target, expected_sha256):
            return target

        if downloader is None:
            raise RuntimeError(
                f"Model '{model_name}' is missing/invalid and no downloader callback was provided."
            )

        downloader(target, progress)
        if not target.exists():
            raise RuntimeError(f"Downloader did not create model file: {target}")
        if not self._is_valid(target, expected_sha256):
            raise RuntimeError(f"Downloaded model checksum mismatch: {target}")
        return target

    def _is_valid(self, path: Path, expected_sha256: str | None) -> bool:
        if not path.exists() or path.stat().st_size == 0:
            return False
        if not expected_sha256:
            return True
        return self.calculate_sha256(path) == expected_sha256.lower().strip()

    def calculate_sha256(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
