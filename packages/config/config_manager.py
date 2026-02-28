from __future__ import annotations

import base64
import json
import os
import secrets
import time
import uuid
from pathlib import Path
from typing import Any

from packages.config.app_paths import ensure_runtime_paths
from packages.config.defaults import DEFAULT_CONFIG
from packages.shared.schemas import AppConfig


class ConfigManager:
    def __init__(self, config_path: Path | None = None) -> None:
        runtime = ensure_runtime_paths()
        self._runtime = runtime
        self.config_path = config_path or runtime.config_path
        self._key_path = runtime.secrets_dir / "fernet.key"
        self._fernet = self._load_or_create_fernet()
        self._ensure_config_exists()

    def get(self) -> AppConfig:
        last_error: Exception | None = None
        for _ in range(5):
            try:
                with self.config_path.open("r", encoding="utf-8") as handle:
                    raw = handle.read()
                if not raw.strip():
                    raise json.JSONDecodeError("empty config", raw, 0)
                data: dict[str, Any] = json.loads(raw)
                return AppConfig.from_dict(data)
            except (FileNotFoundError, json.JSONDecodeError) as exc:
                last_error = exc
                time.sleep(0.05)
        raise RuntimeError(f"Failed reading config: {last_error}")

    def as_dict(self) -> dict[str, Any]:
        return self.get().to_dict()

    def set(self, key: str, value: Any) -> None:
        current = self.as_dict()
        current[key] = value
        self._write(current)

    def set_many(self, data: dict[str, Any]) -> None:
        current = self.as_dict()
        current.update(data)
        self._write(current)

    def save_encrypted_key(self, name: str, api_key: str) -> None:
        if self._fernet is None:
            raise RuntimeError("cryptography is not installed; cannot encrypt API keys")
        encrypted = self._fernet.encrypt(api_key.encode("utf-8")).decode("utf-8")
        self.set(f"ENCRYPTED_{name.upper()}", encrypted)

    def get_encrypted_key(self, name: str) -> str:
        if self._fernet is None:
            raise RuntimeError("cryptography is not installed; cannot decrypt API keys")
        encrypted = self.as_dict().get(f"ENCRYPTED_{name.upper()}", "")
        if not encrypted:
            raise ValueError(f"API key {name} not found")
        decrypted = self._fernet.decrypt(encrypted.encode("utf-8"))
        return decrypted.decode("utf-8")

    def _ensure_config_exists(self) -> None:
        if not self.config_path.exists():
            initial = dict(DEFAULT_CONFIG)
            initial["APP_DATA_PATH"] = str(self._runtime.root)
            self._write(initial)
            return

        # Back-fill missing keys to keep config forward compatible.
        data = self.as_dict()
        changed = False
        for key, value in DEFAULT_CONFIG.items():
            if key not in data:
                data[key] = value
                changed = True
        if not data.get("APP_DATA_PATH"):
            data["APP_DATA_PATH"] = str(self._runtime.root)
            changed = True
        if changed:
            self._write(data)

    def _write(self, data: dict[str, Any]) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.config_path.parent / f"{self.config_path.stem}.{os.getpid()}.{uuid.uuid4().hex}.tmp"
        with temp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        for _ in range(10):
            try:
                os.replace(temp_path, self.config_path)
                return
            except PermissionError:
                time.sleep(0.05)
        # Last attempt lets the original error bubble up.
        os.replace(temp_path, self.config_path)

    def _load_or_create_fernet(self) -> Any:
        try:
            from cryptography.fernet import Fernet  # type: ignore
        except Exception:
            return None

        if not self._key_path.exists():
            self._key_path.write_bytes(Fernet.generate_key())
        key = self._key_path.read_bytes().strip()
        if not key:
            key = Fernet.generate_key()
            self._key_path.write_bytes(key)
        # Defensive fallback if an invalid key somehow exists.
        try:
            return Fernet(key)
        except Exception:
            fresh = base64.urlsafe_b64encode(secrets.token_bytes(32))
            self._key_path.write_bytes(fresh)
            return Fernet(fresh)
