from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from packages.config.app_paths import RuntimePaths, ensure_runtime_paths
from packages.config.logging_setup import get_logger
from services.ai_engine.input_handler import InputSource


@dataclass(slots=True)
class IngestedMedia:
    job_id: str
    source_type: str
    working_dir: Path
    source_video_path: Path
    source_audio_path: Path
    title: str


class VideoIngester:
    """
    Produces standardized source files:
    - source_video.mp4
    - source_audio.wav
    """

    def __init__(self, runtime_paths: RuntimePaths | None = None) -> None:
        self.paths = runtime_paths or ensure_runtime_paths()
        self.logger = get_logger("services.ai_engine.ingester")

    def ingest(self, job_id: str, source: InputSource) -> IngestedMedia:
        job_dir = self.paths.downloads_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        video_out = job_dir / "source_video.mp4"
        audio_out = job_dir / "source_audio.wav"

        if source.source_type == "youtube":
            title = self._ingest_youtube(source.normalized_input, job_dir, video_out)
        elif source.source_type == "local":
            title = self._ingest_local(source, job_dir, video_out)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")

        self._extract_audio(video_out, audio_out)
        return IngestedMedia(
            job_id=job_id,
            source_type=source.source_type,
            working_dir=job_dir,
            source_video_path=video_out,
            source_audio_path=audio_out,
            title=title,
        )

    def _ingest_local(self, source: InputSource, job_dir: Path, video_out: Path) -> str:
        if source.local_path is None:
            raise ValueError("InputSource.local_path is required for local ingestion")
        src = source.local_path
        if src.suffix.lower() == ".mp4":
            shutil.copy2(src, video_out)
        else:
            self._run_command(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(src),
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    str(video_out),
                ]
            )
        return source.display_name

    def _ingest_youtube(self, youtube_url: str, job_dir: Path, video_out: Path) -> str:
        try:
            import yt_dlp  # type: ignore
        except Exception as exc:
            raise RuntimeError("yt-dlp is required for YouTube ingestion") from exc

        outtmpl = str(job_dir / "yt_source.%(ext)s")
        options = {
            "quiet": True,
            "noprogress": True,
            "format": "bestvideo[height<=1080]+bestaudio/best",
            "outtmpl": outtmpl,
            "merge_output_format": "mp4",
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(youtube_url, download=True)

        downloaded_mp4 = sorted(job_dir.glob("yt_source*.mp4"))
        if not downloaded_mp4:
            fallback_any = sorted(job_dir.glob("yt_source*"))
            if not fallback_any:
                raise RuntimeError("yt-dlp did not produce output file")
            self._run_command(["ffmpeg", "-y", "-i", str(fallback_any[-1]), str(video_out)])
        else:
            shutil.move(str(downloaded_mp4[-1]), str(video_out))
        return str(info.get("title") or "youtube_video")

    def _extract_audio(self, video_path: Path, audio_out: Path) -> None:
        self._run_command(
            [
                "ffmpeg",
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-ac",
                "1",
                "-ar",
                "16000",
                "-c:a",
                "pcm_s16le",
                str(audio_out),
            ]
        )

    def _run_command(self, command: list[str]) -> None:
        self.logger.debug("Running command: %s", " ".join(command))
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"Command failed ({result.returncode}): {' '.join(command)}\n{result.stderr.strip()}"
            )
