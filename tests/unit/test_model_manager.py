from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from packages.config.model_manager import ModelManager


def test_ensure_model_with_downloader(tmp_path: Path) -> None:
    manager = ModelManager(model_root=tmp_path)

    def downloader(target: Path, _progress) -> None:
        target.write_bytes(b"weights")

    digest = hashlib.sha256(b"weights").hexdigest()
    model = manager.ensure_model("small", downloader=downloader, expected_sha256=digest)
    assert model.exists()
    assert model.name == "small.bin"


def test_ensure_model_raises_without_downloader(tmp_path: Path) -> None:
    manager = ModelManager(model_root=tmp_path)
    with pytest.raises(RuntimeError):
        manager.ensure_model("small", expected_sha256="abc")
