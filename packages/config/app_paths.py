from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "AutoClipper"


@dataclass(slots=True)
class RuntimePaths:
    root: Path
    logs_dir: Path
    storage_dir: Path
    downloads_dir: Path
    clips_dir: Path
    models_dir: Path
    temp_dir: Path
    secrets_dir: Path
    config_path: Path
    database_path: Path


def get_app_data_root(app_name: str = APP_NAME) -> Path:
    override = os.getenv("AUTOCLIPPER_APPDATA")
    if override:
        return Path(override).expanduser()

    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        base_dir = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
    else:
        base_dir = Path.home() / ".config"
    return base_dir / app_name


def ensure_runtime_paths(app_name: str = APP_NAME) -> RuntimePaths:
    root = _resolve_writable_root(app_name)
    logs_dir = root / "logs"
    storage_dir = root / "storage"
    downloads_dir = storage_dir / "downloads"
    clips_dir = storage_dir / "clips"
    models_dir = storage_dir / "models"
    temp_dir = storage_dir / "temp"
    secrets_dir = root / "secrets"
    config_path = root / "config.json"
    database_path = root / "database.db"

    for directory in (
        root,
        logs_dir,
        storage_dir,
        downloads_dir,
        clips_dir,
        models_dir,
        temp_dir,
        secrets_dir,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    return RuntimePaths(
        root=root,
        logs_dir=logs_dir,
        storage_dir=storage_dir,
        downloads_dir=downloads_dir,
        clips_dir=clips_dir,
        models_dir=models_dir,
        temp_dir=temp_dir,
        secrets_dir=secrets_dir,
        config_path=config_path,
        database_path=database_path,
    )


def _resolve_writable_root(app_name: str) -> Path:
    preferred = get_app_data_root(app_name)
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / ".write_test"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return preferred
    except PermissionError:
        repo_root = Path(__file__).resolve().parents[2]
        fallback = repo_root / ".autoclipper-runtime"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
