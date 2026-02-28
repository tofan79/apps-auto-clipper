from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from packages.shared.security import sanitize_filename


YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "youtu.be",
    "www.youtu.be",
}
ALLOWED_LOCAL_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}


@dataclass(slots=True)
class InputSource:
    source_type: str  # youtube | local
    raw_input: str
    normalized_input: str
    display_name: str
    local_path: Path | None = None


class InputHandler:
    """
    Validates and normalizes user input (YouTube URL or local file).
    """

    def __init__(self, *, max_local_file_gb: int = 25) -> None:
        self.max_local_file_bytes = max_local_file_gb * 1024**3

    def normalize(self, raw_input: str) -> InputSource:
        raw = raw_input.strip()
        if not raw:
            raise ValueError("Input source cannot be empty")

        if self._looks_like_youtube(raw):
            normalized = self._normalize_youtube_url(raw)
            return InputSource(
                source_type="youtube",
                raw_input=raw_input,
                normalized_input=normalized,
                display_name=sanitize_filename(normalized, default="youtube_video"),
            )

        local_path = Path(raw).expanduser()
        return self._normalize_local_path(local_path, raw_input)

    def _normalize_local_path(self, local_path: Path, raw_input: str) -> InputSource:
        if not local_path.exists():
            raise ValueError(f"Local file does not exist: {local_path}")
        if not local_path.is_file():
            raise ValueError(f"Input must be a file: {local_path}")
        if local_path.suffix.lower() not in ALLOWED_LOCAL_EXTENSIONS:
            raise ValueError(
                f"Unsupported file extension '{local_path.suffix}'. Allowed: {sorted(ALLOWED_LOCAL_EXTENSIONS)}"
            )
        if local_path.stat().st_size == 0:
            raise ValueError("Local file is empty")
        if local_path.stat().st_size > self.max_local_file_bytes:
            raise ValueError("Local file exceeds max supported size")

        resolved = local_path.resolve()
        return InputSource(
            source_type="local",
            raw_input=raw_input,
            normalized_input=str(resolved),
            display_name=sanitize_filename(resolved.stem, default="local_video"),
            local_path=resolved,
        )

    def _looks_like_youtube(self, raw: str) -> bool:
        parsed = urlparse(raw)
        return parsed.scheme in {"http", "https"} and parsed.netloc.lower() in YOUTUBE_HOSTS

    def _normalize_youtube_url(self, raw: str) -> str:
        parsed = urlparse(raw)
        host = parsed.netloc.lower()
        if host not in YOUTUBE_HOSTS:
            raise ValueError("Unsupported YouTube host")

        if host.endswith("youtu.be"):
            video_id = parsed.path.strip("/")
        else:
            query = parse_qs(parsed.query)
            video_id = (query.get("v") or [""])[0]

        if not re.fullmatch(r"[A-Za-z0-9_-]{6,20}", video_id or ""):
            raise ValueError("Invalid YouTube video ID")
        return f"https://www.youtube.com/watch?v={video_id}"
