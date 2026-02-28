from __future__ import annotations

from pathlib import Path

import pytest

from packages.shared.security import sanitize_file_path, sanitize_filename


def test_sanitize_filename_keeps_safe_chars() -> None:
    assert sanitize_filename("my*video:01?.mp4") == "my_video_01_.mp4"


def test_sanitize_filename_falls_back_when_empty() -> None:
    assert sanitize_filename("   ...   ", default="clip") == "clip"


def test_sanitize_file_path_accepts_child_path(tmp_path: Path) -> None:
    base = tmp_path / "base"
    base.mkdir(parents=True)
    child = base / "child.txt"
    child.write_text("ok", encoding="utf-8")
    resolved = sanitize_file_path(child, base_dir=base)
    assert resolved == child.resolve()


def test_sanitize_file_path_rejects_path_traversal(tmp_path: Path) -> None:
    base = tmp_path / "base"
    outside = tmp_path / "outside.txt"
    base.mkdir(parents=True)
    outside.write_text("nope", encoding="utf-8")
    with pytest.raises(ValueError):
        sanitize_file_path(outside, base_dir=base)
