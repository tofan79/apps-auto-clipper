from __future__ import annotations

import multiprocessing
from dataclasses import dataclass


@dataclass(slots=True)
class SystemProfile:
    name: str
    whisper_model: str
    whisper_compute: str
    ffmpeg_preset: str
    ffmpeg_threads: int
    max_concurrent_jobs: int
    chunk_duration: int
    ram_limit_gb: float


def detect_profile() -> SystemProfile:
    """
    Auto-detect safe processing profile.
    Priority: stability first, speed second.
    """
    ram_gb = _detect_ram_gb()
    cpu_cores = multiprocessing.cpu_count()

    if ram_gb < 10 and cpu_cores <= 4:
        return SystemProfile(
            name="minimum",
            whisper_model="tiny",
            whisper_compute="int8",
            ffmpeg_preset="ultrafast",
            ffmpeg_threads=2,
            max_concurrent_jobs=1,
            chunk_duration=1800,
            ram_limit_gb=5.0,
        )
    if ram_gb < 20:
        return SystemProfile(
            name="standard",
            whisper_model="small",
            whisper_compute="float16",
            ffmpeg_preset="fast",
            ffmpeg_threads=4,
            max_concurrent_jobs=1,
            chunk_duration=3600,
            ram_limit_gb=10.0,
        )
    return SystemProfile(
        name="high",
        whisper_model="medium",
        whisper_compute="float16",
        ffmpeg_preset="veryfast",
        ffmpeg_threads=0,
        max_concurrent_jobs=2,
        chunk_duration=7200,
        ram_limit_gb=20.0,
    )


def _detect_ram_gb() -> float:
    try:
        import psutil  # type: ignore

        return psutil.virtual_memory().total / (1024**3)
    except Exception:
        # Conservative fallback if psutil is not installed.
        return 8.0
