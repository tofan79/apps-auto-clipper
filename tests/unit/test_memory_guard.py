from __future__ import annotations

import pytest

from packages.config.memory_guard import MemoryGuard


def test_check_returns_true_when_memory_is_safe(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.memory_guard._process_rss_bytes", lambda: 200 * 1024**2)
    monkeypatch.setattr("packages.config.memory_guard.time.sleep", lambda _x: None)

    guard = MemoryGuard(limit_gb=1.0, warning_threshold=0.85)
    assert guard.check("unit-test") is True


def test_check_returns_false_when_memory_is_critical(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.memory_guard._process_rss_bytes", lambda: int(0.97 * 1024**3))
    monkeypatch.setattr("packages.config.memory_guard.time.sleep", lambda _x: None)

    guard = MemoryGuard(limit_gb=1.0, warning_threshold=0.85)
    assert guard.check("unit-test") is False


def test_wait_until_safe_raises_after_timeout(monkeypatch) -> None:
    monkeypatch.setattr("packages.config.memory_guard._process_rss_bytes", lambda: int(0.99 * 1024**3))
    monkeypatch.setattr("packages.config.memory_guard.time.sleep", lambda _x: None)

    guard = MemoryGuard(limit_gb=1.0, warning_threshold=0.85)
    with pytest.raises(MemoryError):
        guard.wait_until_safe(timeout=0)
