from __future__ import annotations

from pathlib import Path

import pytest

from services.ai_engine.input_handler import InputHandler


def test_normalize_youtube_url_short_form() -> None:
    handler = InputHandler()
    source = handler.normalize("https://youtu.be/dQw4w9WgXcQ")
    assert source.source_type == "youtube"
    assert source.normalized_input == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


def test_normalize_local_file(tmp_path: Path) -> None:
    local = tmp_path / "sample.mp4"
    local.write_bytes(b"fake")
    handler = InputHandler()
    source = handler.normalize(str(local))
    assert source.source_type == "local"
    assert source.local_path == local.resolve()


def test_normalize_rejects_bad_extension(tmp_path: Path) -> None:
    local = tmp_path / "sample.txt"
    local.write_text("fake", encoding="utf-8")
    handler = InputHandler()
    with pytest.raises(ValueError):
        handler.normalize(str(local))
