from __future__ import annotations

from pathlib import Path

from packages.config import app_paths


def test_get_app_data_root_uses_override(monkeypatch, tmp_path: Path) -> None:
    custom = tmp_path / "runtime-root"
    monkeypatch.setenv("AUTOCLIPPER_APPDATA", str(custom))

    resolved = app_paths.get_app_data_root()
    assert resolved == custom


def test_ensure_runtime_paths_creates_expected_directories(monkeypatch, tmp_path: Path) -> None:
    custom = tmp_path / "autoclipper-root"
    monkeypatch.setenv("AUTOCLIPPER_APPDATA", str(custom))

    paths = app_paths.ensure_runtime_paths()

    assert paths.root == custom
    assert paths.logs_dir.exists()
    assert paths.storage_dir.exists()
    assert paths.downloads_dir.exists()
    assert paths.clips_dir.exists()
    assert paths.models_dir.exists()
    assert paths.temp_dir.exists()
    assert paths.secrets_dir.exists()
    assert paths.config_path == custom / "config.json"
    assert paths.database_path == custom / "database.db"
