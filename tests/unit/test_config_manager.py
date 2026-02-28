from __future__ import annotations

from pathlib import Path

import pytest

from packages.config.app_paths import RuntimePaths
from packages.config.config_manager import ConfigManager


def _runtime_paths(base: Path) -> RuntimePaths:
    return RuntimePaths(
        root=base,
        logs_dir=base / "logs",
        storage_dir=base / "storage",
        downloads_dir=base / "storage" / "downloads",
        clips_dir=base / "storage" / "clips",
        models_dir=base / "storage" / "models",
        temp_dir=base / "storage" / "temp",
        secrets_dir=base / "secrets",
        config_path=base / "config.json",
        database_path=base / "database.db",
    )


def _ensure_tree(paths: RuntimePaths) -> None:
    for item in (
        paths.root,
        paths.logs_dir,
        paths.storage_dir,
        paths.downloads_dir,
        paths.clips_dir,
        paths.models_dir,
        paths.temp_dir,
        paths.secrets_dir,
    ):
        item.mkdir(parents=True, exist_ok=True)


def test_config_manager_creates_default_config(monkeypatch, tmp_path: Path) -> None:
    runtime = _runtime_paths(tmp_path / "runtime-a")
    _ensure_tree(runtime)
    monkeypatch.setattr(
        "packages.config.config_manager.ensure_runtime_paths",
        lambda: runtime,
    )

    manager = ConfigManager()
    cfg = manager.get()

    assert runtime.config_path.exists()
    assert cfg.APP_DATA_PATH == str(runtime.root)
    assert cfg.MAX_CLIPS == 10


def test_config_manager_set_updates_values(monkeypatch, tmp_path: Path) -> None:
    runtime = _runtime_paths(tmp_path / "runtime-b")
    _ensure_tree(runtime)
    monkeypatch.setattr(
        "packages.config.config_manager.ensure_runtime_paths",
        lambda: runtime,
    )

    manager = ConfigManager()
    manager.set("MAX_CLIPS", 7)
    manager.set_many({"LAN_ENABLED": True, "FFMPEG_PRESET": "fast"})

    cfg = manager.get()
    assert cfg.MAX_CLIPS == 7
    assert cfg.LAN_ENABLED is True
    assert cfg.FFMPEG_PRESET == "fast"


def test_config_manager_encrypted_key_roundtrip(monkeypatch, tmp_path: Path) -> None:
    class FakeFernet:
        def encrypt(self, payload: bytes) -> bytes:
            return b"enc:" + payload

        def decrypt(self, payload: bytes) -> bytes:
            if not payload.startswith(b"enc:"):
                raise ValueError("bad token")
            return payload[4:]

    runtime = _runtime_paths(tmp_path / "runtime-c")
    _ensure_tree(runtime)
    monkeypatch.setattr(
        "packages.config.config_manager.ensure_runtime_paths",
        lambda: runtime,
    )
    monkeypatch.setattr(
        ConfigManager,
        "_load_or_create_fernet",
        lambda self: FakeFernet(),
    )

    manager = ConfigManager()
    manager.save_encrypted_key("openrouter", "secret-key")

    raw = manager.as_dict()["ENCRYPTED_OPENROUTER"]
    assert raw != "secret-key"
    assert raw.startswith("enc:")
    assert manager.get_encrypted_key("openrouter") == "secret-key"


def test_config_manager_raises_when_crypto_unavailable(monkeypatch, tmp_path: Path) -> None:
    runtime = _runtime_paths(tmp_path / "runtime-d")
    _ensure_tree(runtime)
    monkeypatch.setattr(
        "packages.config.config_manager.ensure_runtime_paths",
        lambda: runtime,
    )
    monkeypatch.setattr(
        ConfigManager,
        "_load_or_create_fernet",
        lambda self: None,
    )

    manager = ConfigManager()
    with pytest.raises(RuntimeError):
        manager.save_encrypted_key("openrouter", "secret-key")
