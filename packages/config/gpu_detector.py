from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class GPUInfo:
    available: bool
    name: str = ""
    vram_mb: int = 0
    device: str = "cpu"


def detect_gpu() -> GPUInfo:
    """
    Auto-detect NVIDIA GPU using nvidia-smi.
    Safe fallback is always CPU.
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return GPUInfo(available=False, device="cpu")

    if result.returncode != 0 or not result.stdout.strip():
        return GPUInfo(available=False, device="cpu")

    first_line = result.stdout.strip().splitlines()[0]
    parts = [part.strip() for part in first_line.split(",", 1)]
    name = parts[0] if parts else ""
    try:
        vram_mb = int(parts[1]) if len(parts) > 1 else 0
    except ValueError:
        vram_mb = 0
    return GPUInfo(available=True, name=name, vram_mb=vram_mb, device="cuda")


def get_whisper_device() -> str:
    return detect_gpu().device
