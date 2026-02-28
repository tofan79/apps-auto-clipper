from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class AppConfig:
    AI_MODE: str = "offline"
    LLM_PROVIDER: str = "ollama"
    OLLAMA_MODEL: str = "llama3.2:3b"
    WHISPER_MODEL: str = "small"
    WHISPER_DEVICE: str = "auto"
    MAX_CLIPS: int = 10
    MIN_VIRAL_SCORE: int = 60
    MAX_CONCURRENT_JOBS: int = 1
    GPU_ENABLED: str = "auto"
    LAN_ENABLED: bool = False
    LAN_TOKEN: str = ""
    FFMPEG_PRESET: str = "veryfast"
    OUTPUT_FORMAT: str = "mp4"
    APP_DATA_PATH: str = ""
    LOG_LEVEL: str = "INFO"
    AUTO_START: bool = False
    ENCRYPTED_OPENROUTER: str = ""
    ENCRYPTED_OPENAI: str = ""

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppConfig":
        valid_keys = {field.name for field in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
