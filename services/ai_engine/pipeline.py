from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.ai_engine.adaptive_renderer import AdaptiveClipRenderer
from services.ai_engine.face_analyzer import FaceAnalyzer, SegmentDecision
from services.ai_engine.hook_detector import HookCandidate, ViralHookDetector
from services.ai_engine.ingester import IngestedMedia, VideoIngester
from services.ai_engine.input_handler import InputHandler
from services.ai_engine.metadata_generator import PlatformMetadata, PlatformMetadataGenerator
from services.ai_engine.providers.base import BaseLLMProvider
from services.ai_engine.subtitle_generator import SubtitleGenerator
from services.ai_engine.transcriber import Transcriber, WordTimestamp


@dataclass(slots=True)
class PipelineArtifacts:
    job_id: str
    clip_path: Path
    subtitle_path: Path
    selected_hook: HookCandidate | None
    segments: list[SegmentDecision]
    metadata: dict[str, PlatformMetadata]


class ClipPipeline:
    """
    Stage 4 orchestration:
    ingest -> transcribe -> hook score -> face analyze -> render -> metadata.
    """

    def __init__(
        self,
        *,
        input_handler: InputHandler | None = None,
        ingester: VideoIngester | None = None,
        transcriber: Transcriber | None = None,
        hook_detector: ViralHookDetector | None = None,
        face_analyzer: FaceAnalyzer | None = None,
        renderer: AdaptiveClipRenderer | None = None,
        subtitle_generator: SubtitleGenerator | None = None,
        metadata_generator: PlatformMetadataGenerator | None = None,
        provider: BaseLLMProvider | None = None,
    ) -> None:
        self.input_handler = input_handler or InputHandler()
        self.ingester = ingester or VideoIngester()
        self.transcriber = transcriber or Transcriber()
        self.hook_detector = hook_detector or ViralHookDetector()
        self.face_analyzer = face_analyzer or FaceAnalyzer()
        self.renderer = renderer or AdaptiveClipRenderer()
        self.subtitle_generator = subtitle_generator or SubtitleGenerator()
        self.metadata_generator = metadata_generator or PlatformMetadataGenerator()
        self.provider = provider

    def run(self, *, job_id: str, raw_input: str) -> PipelineArtifacts:
        source = self.input_handler.normalize(raw_input)
        media = self.ingester.ingest(job_id, source)
        words = self.transcriber.transcribe(media.source_audio_path)
        if not words:
            raise RuntimeError("Transcriber returned no words")

        transcript_text = self._build_transcript_text(words)
        selected_hook = self._select_hook(words=words, transcript_text=transcript_text)
        clip_start, clip_end = self._resolve_clip_window(words=words, selected_hook=selected_hook)

        segments = self.face_analyzer.analyze(frame_samples=[], clip_start=clip_start, clip_end=clip_end)
        clip_words = [item for item in words if item.start >= clip_start and item.end <= clip_end] or words

        subtitle_path = media.working_dir / "clip_01.ass"
        self.subtitle_generator.generate_ass(words=clip_words, output_path=subtitle_path)

        clip_path = media.working_dir / "clip_01.mp4"
        self.renderer.render_clip(
            source_video=media.source_video_path,
            segments=segments,
            output_path=clip_path,
            subtitle_path=subtitle_path,
        )

        metadata = self.metadata_generator.generate_for_platforms(
            transcript_text=transcript_text,
            base_title=media.title,
            provider=self.provider,
            clip_index=1,
        )
        return PipelineArtifacts(
            job_id=job_id,
            clip_path=clip_path,
            subtitle_path=subtitle_path,
            selected_hook=selected_hook,
            segments=segments,
            metadata=metadata,
        )

    def _build_transcript_text(self, words: list[WordTimestamp]) -> str:
        return " ".join(item.word for item in words).strip()

    def _select_hook(self, *, words: list[WordTimestamp], transcript_text: str) -> HookCandidate | None:
        if self.provider is None:
            return None
        try:
            llm_hooks = self.provider.generate_hooks(transcript_text, max_candidates=10)
        except Exception:
            return None
        candidates = self.hook_detector.detect(
            words=words,
            llm_hooks=llm_hooks,
            max_clips=1,
            min_viral_score=0,
        )
        return candidates[0] if candidates else None

    def _resolve_clip_window(
        self,
        *,
        words: list[WordTimestamp],
        selected_hook: HookCandidate | None,
    ) -> tuple[float, float]:
        if selected_hook is not None:
            return selected_hook.start, selected_hook.end

        start = min(item.start for item in words)
        end = max(item.end for item in words)
        max_duration = 45.0
        if (end - start) <= max_duration:
            return start, end
        return start, start + max_duration
