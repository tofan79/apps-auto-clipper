from __future__ import annotations

from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "AI_MODE": "offline",
    "LLM_PROVIDER": "ollama",
    "OLLAMA_MODEL": "llama3.2:3b",
    "OPENROUTER_MODEL": "openrouter/auto",
    "WHISPER_MODEL": "small",
    "WHISPER_DEVICE": "auto",
    "MAX_CLIPS": 10,
    "MIN_VIRAL_SCORE": 60,
    "MAX_CONCURRENT_JOBS": 1,
    "GPU_ENABLED": "auto",
    "LAN_ENABLED": False,
    "LAN_TOKEN": "",
    "FFMPEG_PRESET": "veryfast",
    "OUTPUT_FORMAT": "mp4",
    "APP_DATA_PATH": "",
    "LOG_LEVEL": "INFO",
    "AUTO_START": False,
    "ENCRYPTED_OPENROUTER": "",
    "ENCRYPTED_OPENAI": "",
}
