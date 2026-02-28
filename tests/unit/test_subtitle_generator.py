from __future__ import annotations

from pathlib import Path

import pytest

from services.ai_engine.subtitle_generator import SubtitleGenerator
from services.ai_engine.transcriber import WordTimestamp


def test_subtitle_generator_writes_ass_with_karaoke_tags(tmp_path: Path) -> None:
    generator = SubtitleGenerator()
    words = [
        WordTimestamp(word="Halo", start=0.0, end=0.4, probability=0.9),
        WordTimestamp(word="semua", start=0.4, end=0.8, probability=0.9),
        WordTimestamp(word="ini", start=0.8, end=1.0, probability=0.9),
        WordTimestamp(word="test", start=1.0, end=1.4, probability=0.9),
    ]
    target = tmp_path / "subtitle.ass"
    output = generator.generate_ass(words=words, output_path=target)
    assert output == target
    content = target.read_text(encoding="utf-8")
    assert "[Events]" in content
    assert "{\\k" in content
    assert "Dialogue: 0," in content


def test_subtitle_generator_rejects_empty_words(tmp_path: Path) -> None:
    generator = SubtitleGenerator()
    with pytest.raises(ValueError):
        generator.generate_ass(words=[], output_path=tmp_path / "subtitle.ass")
