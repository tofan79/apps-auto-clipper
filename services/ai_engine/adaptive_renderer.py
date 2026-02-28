from __future__ import annotations

import shutil
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path

from services.ai_engine.face_analyzer import SegmentDecision


@dataclass(slots=True)
class RenderedSegment:
    start: float
    end: float
    mode: str
    path: Path


class FfmpegCommandBuilder:
    def __init__(self, *, width: int = 1080, height: int = 1920, preset: str = "veryfast") -> None:
        self.width = width
        self.height = height
        self.preset = preset

    def build_segment_command(self, *, source_video: Path, segment: SegmentDecision, output_path: Path) -> list[str]:
        if segment.mode == "portrait":
            return self._portrait_command(source_video=source_video, segment=segment, output_path=output_path)
        return self._landscape_blur_command(source_video=source_video, segment=segment, output_path=output_path)

    def build_concat_command(self, *, concat_file: Path, output_path: Path) -> list[str]:
        return [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(output_path),
        ]

    def build_subtitle_burn_command(self, *, source_video: Path, subtitle_path: Path, output_path: Path) -> list[str]:
        subtitle_expr = str(subtitle_path).replace("\\", "/").replace(":", "\\:")
        return [
            "ffmpeg",
            "-y",
            "-i",
            str(source_video),
            "-vf",
            f"ass='{subtitle_expr}'",
            "-c:v",
            "libx264",
            "-preset",
            self.preset,
            "-c:a",
            "aac",
            str(output_path),
        ]

    def _portrait_command(self, *, source_video: Path, segment: SegmentDecision, output_path: Path) -> list[str]:
        crop_filter = (
            "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)':"
            f"x='max(0,min(iw-ow,{segment.crop_center_x:.6f}*iw-ow/2))':"
            f"y='max(0,min(ih-oh,{segment.crop_center_y:.6f}*ih-oh/2))',"
            f"scale={self.width}:{self.height},setsar=1"
        )
        return [
            "ffmpeg",
            "-y",
            "-ss",
            f"{segment.start:.3f}",
            "-to",
            f"{segment.end:.3f}",
            "-i",
            str(source_video),
            "-vf",
            crop_filter,
            "-c:v",
            "libx264",
            "-preset",
            self.preset,
            "-crf",
            "21",
            "-c:a",
            "aac",
            str(output_path),
        ]

    def _landscape_blur_command(self, *, source_video: Path, segment: SegmentDecision, output_path: Path) -> list[str]:
        filter_complex = (
            f"[0:v]scale={self.width}:{self.height}:force_original_aspect_ratio=increase,boxblur=20:10[bg];"
            f"[0:v]scale={self.width}:{self.height}:force_original_aspect_ratio=decrease[fg];"
            "[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1[v]"
        )
        return [
            "ffmpeg",
            "-y",
            "-ss",
            f"{segment.start:.3f}",
            "-to",
            f"{segment.end:.3f}",
            "-i",
            str(source_video),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            self.preset,
            "-crf",
            "22",
            "-c:a",
            "aac",
            str(output_path),
        ]


class AdaptiveClipRenderer:
    """
    Orchestrates segment render -> concat -> subtitle burn.
    """

    def __init__(self, command_builder: FfmpegCommandBuilder | None = None) -> None:
        self.builder = command_builder or FfmpegCommandBuilder()

    def render_clip(
        self,
        *,
        source_video: Path,
        segments: list[SegmentDecision],
        output_path: Path,
        subtitle_path: Path | None = None,
    ) -> Path:
        if not segments:
            raise ValueError("segments cannot be empty")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_dir = output_path.parent / f".autoclipper-render-{uuid.uuid4().hex}"
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            rendered = self.render_segments(source_video=source_video, segments=segments, temp_dir=temp_dir)
            concat_output = temp_dir / "concat.mp4"
            self.concat_segments(segments=rendered, output_path=concat_output, temp_dir=temp_dir)

            if subtitle_path is None:
                shutil.copy2(concat_output, output_path)
                return output_path

            command = self.builder.build_subtitle_burn_command(
                source_video=concat_output,
                subtitle_path=subtitle_path,
                output_path=output_path,
            )
            self._run_command(command)
            return output_path
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def render_segments(
        self,
        *,
        source_video: Path,
        segments: list[SegmentDecision],
        temp_dir: Path,
    ) -> list[RenderedSegment]:
        rendered: list[RenderedSegment] = []
        for index, segment in enumerate(segments):
            target = temp_dir / f"segment_{index:03d}.mp4"
            command = self.builder.build_segment_command(source_video=source_video, segment=segment, output_path=target)
            self._run_command(command)
            rendered.append(
                RenderedSegment(
                    start=segment.start,
                    end=segment.end,
                    mode=segment.mode,
                    path=target,
                )
            )
        return rendered

    def concat_segments(self, *, segments: list[RenderedSegment], output_path: Path, temp_dir: Path) -> None:
        concat_file = temp_dir / "concat.txt"
        lines = [f"file '{item.path.as_posix()}'" for item in segments]
        concat_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
        command = self.builder.build_concat_command(concat_file=concat_file, output_path=output_path)
        self._run_command(command)

    def _run_command(self, command: list[str]) -> None:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
            )
