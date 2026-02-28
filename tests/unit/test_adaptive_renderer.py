from __future__ import annotations

from pathlib import Path

from services.ai_engine.adaptive_renderer import AdaptiveClipRenderer, FfmpegCommandBuilder
from services.ai_engine.face_analyzer import SegmentDecision


class _FakeRenderer(AdaptiveClipRenderer):
    def _run_command(self, command: list[str]) -> None:
        output = Path(command[-1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"ok")


def test_command_builder_builds_portrait_and_landscape_filters(tmp_path: Path) -> None:
    builder = FfmpegCommandBuilder()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")

    portrait = SegmentDecision(0.0, 2.0, "portrait", 0.55, 0.45, 1)
    landscape = SegmentDecision(2.0, 4.0, "landscape_blur", 0.50, 0.50, 2)
    cmd_portrait = builder.build_segment_command(source_video=source, segment=portrait, output_path=tmp_path / "p.mp4")
    cmd_landscape = builder.build_segment_command(source_video=source, segment=landscape, output_path=tmp_path / "l.mp4")
    assert "-vf" in cmd_portrait
    assert "-filter_complex" in cmd_landscape


def test_renderer_orchestrates_segments_concat_and_subtitles(tmp_path: Path) -> None:
    renderer = _FakeRenderer()
    source = tmp_path / "source.mp4"
    source.write_bytes(b"video")
    subtitle = tmp_path / "subtitle.ass"
    subtitle.write_text("[Events]\n", encoding="utf-8")

    output = tmp_path / "clip.mp4"
    segments = [
        SegmentDecision(0.0, 1.0, "portrait", 0.50, 0.50, 1),
        SegmentDecision(1.0, 2.0, "landscape_blur", 0.50, 0.50, 2),
    ]
    rendered = renderer.render_clip(source_video=source, segments=segments, output_path=output, subtitle_path=subtitle)
    assert rendered == output
    assert output.exists()
