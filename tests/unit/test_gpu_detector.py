from __future__ import annotations

import subprocess

from packages.config.gpu_detector import detect_gpu, get_whisper_device


class _Completed:
    def __init__(self, returncode: int, stdout: str) -> None:
        self.returncode = returncode
        self.stdout = stdout


def test_detect_gpu_returns_cuda_when_nvidia_smi_succeeds(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: _Completed(0, "NVIDIA RTX 3050, 4096\n"),
    )

    info = detect_gpu()
    assert info.available is True
    assert info.name == "NVIDIA RTX 3050"
    assert info.vram_mb == 4096
    assert info.device == "cuda"


def test_detect_gpu_returns_cpu_when_command_missing(monkeypatch) -> None:
    def _raise(*args, **kwargs):
        raise FileNotFoundError("nvidia-smi not found")

    monkeypatch.setattr(subprocess, "run", _raise)

    info = detect_gpu()
    assert info.available is False
    assert info.device == "cpu"
    assert get_whisper_device() == "cpu"


def test_detect_gpu_returns_cpu_on_nonzero_exit(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: _Completed(1, ""),
    )

    info = detect_gpu()
    assert info.available is False
    assert info.device == "cpu"
