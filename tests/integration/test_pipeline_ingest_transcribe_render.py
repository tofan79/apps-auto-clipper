from __future__ import annotations

from pathlib import Path

from services.ai_engine.face_analyzer import SegmentDecision
from services.ai_engine.ingester import IngestedMedia
from services.ai_engine.input_handler import InputHandler, InputSource
from services.ai_engine.metadata_generator import PlatformMetadataGenerator
from services.ai_engine.pipeline import ClipPipeline
from services.ai_engine.providers.base import BaseLLMProvider
from services.ai_engine.subtitle_generator import SubtitleGenerator
from services.ai_engine.transcriber import WordTimestamp
from services.ai_engine.adaptive_renderer import AdaptiveClipRenderer


class _FakeIngester:
    def __init__(self, root: Path) -> None:
        self.root = root

    def ingest(self, job_id: str, source: InputSource) -> IngestedMedia:
        job_dir = self.root / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        source_video = job_dir / "source_video.mp4"
        source_audio = job_dir / "source_audio.wav"
        if source.local_path is None:
            raise RuntimeError("local_path is required")
        source_video.write_bytes(source.local_path.read_bytes())
        source_audio.write_bytes(b"fake-audio")
        return IngestedMedia(
            job_id=job_id,
            source_type=source.source_type,
            working_dir=job_dir,
            source_video_path=source_video,
            source_audio_path=source_audio,
            title=source.display_name,
        )


class _FakeTranscriber:
    def transcribe(self, audio_path: Path) -> list[WordTimestamp]:
        _ = audio_path
        return [
            WordTimestamp(word="ini", start=0.0, end=0.3, probability=0.9),
            WordTimestamp(word="contoh", start=0.3, end=0.7, probability=0.9),
            WordTimestamp(word="clip", start=0.7, end=1.1, probability=0.9),
            WordTimestamp(word="viral", start=1.1, end=1.5, probability=0.9),
            WordTimestamp(word="untuk", start=1.5, end=1.9, probability=0.9),
            WordTimestamp(word="testing", start=1.9, end=2.5, probability=0.9),
        ]


class _FakeProvider(BaseLLMProvider):
    def health_check(self) -> bool:
        return True

    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict]:
        _ = transcript_text
        _ = max_candidates
        return [
            {
                "start": 0.0,
                "end": 2.5,
                "semantic_score": 0.9,
                "emotion_score": 0.9,
                "confidence": 0.8,
                "reason": "high energy",
            }
        ]

    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict:
        _ = transcript_text
        return {
            "title": f"{platform.title()} Title",
            "caption": f"{platform} caption",
            "hashtags": [platform, "shorts", "autoclipper"],
        }


class _FakeRenderer(AdaptiveClipRenderer):
    def render_clip(
        self,
        *,
        source_video: Path,
        segments: list[SegmentDecision],
        output_path: Path,
        subtitle_path: Path | None = None,
    ) -> Path:
        _ = source_video
        _ = segments
        _ = subtitle_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"rendered")
        return output_path


def test_pipeline_integration_ingest_transcribe_render(tmp_path: Path) -> None:
    local_video = tmp_path / "sample_short.mp4"
    local_video.write_bytes(b"fake-video")

    pipeline = ClipPipeline(
        input_handler=InputHandler(),
        ingester=_FakeIngester(tmp_path),
        transcriber=_FakeTranscriber(),
        renderer=_FakeRenderer(),  # type: ignore[arg-type]
        subtitle_generator=SubtitleGenerator(),
        metadata_generator=PlatformMetadataGenerator(),
        provider=_FakeProvider(),
    )
    result = pipeline.run(job_id="job-stage4-it", raw_input=str(local_video))

    assert result.clip_path.exists()
    assert result.subtitle_path.exists()
    assert result.selected_hook is not None
    assert result.segments
    assert "tiktok" in result.metadata
    assert result.metadata["tiktok"].title == "Tiktok Title"
