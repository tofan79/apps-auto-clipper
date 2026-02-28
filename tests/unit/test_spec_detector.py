from __future__ import annotations

import multiprocessing

from packages.config.spec_detector import detect_profile


def test_detect_profile_minimum(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.spec_detector._detect_ram_gb", lambda: 8.0)
    monkeypatch.setattr(multiprocessing, "cpu_count", lambda: 4)

    profile = detect_profile()
    assert profile.name == "minimum"
    assert profile.whisper_model == "tiny"
    assert profile.chunk_duration == 1800


def test_detect_profile_standard(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.spec_detector._detect_ram_gb", lambda: 16.0)
    monkeypatch.setattr(multiprocessing, "cpu_count", lambda: 8)

    profile = detect_profile()
    assert profile.name == "standard"
    assert profile.whisper_model == "small"
    assert profile.ffmpeg_threads == 4


def test_detect_profile_high(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.spec_detector._detect_ram_gb", lambda: 24.0)
    monkeypatch.setattr(multiprocessing, "cpu_count", lambda: 8)

    profile = detect_profile()
    assert profile.name == "high"
    assert profile.whisper_model == "medium"
    assert profile.max_concurrent_jobs == 2
