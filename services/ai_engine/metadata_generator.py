from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from packages.shared.security import sanitize_filename
from services.ai_engine.providers.base import BaseLLMProvider


PLATFORMS = ("youtube", "tiktok", "instagram", "facebook")


@dataclass(slots=True)
class PlatformMetadata:
    title: str
    caption: str
    hashtags: list[str]
    filename: str


class PlatformMetadataGenerator:
    def __init__(self, *, max_title_chars: int = 80) -> None:
        self.max_title_chars = max(20, max_title_chars)

    def generate_for_platforms(
        self,
        *,
        transcript_text: str,
        base_title: str,
        provider: BaseLLMProvider | None,
        clip_index: int,
    ) -> dict[str, PlatformMetadata]:
        output: dict[str, PlatformMetadata] = {}
        for platform in PLATFORMS:
            meta = self._generate_single(
                platform=platform,
                transcript_text=transcript_text,
                base_title=base_title,
                provider=provider,
                clip_index=clip_index,
            )
            output[platform] = meta
        return output

    def _generate_single(
        self,
        *,
        platform: str,
        transcript_text: str,
        base_title: str,
        provider: BaseLLMProvider | None,
        clip_index: int,
    ) -> PlatformMetadata:
        payload: dict[str, Any] = {}
        if provider is not None:
            try:
                payload = provider.generate_metadata(transcript_text=transcript_text, platform=platform)
            except Exception:
                payload = {}

        title = str(payload.get("title") or "").strip() or self._fallback_title(base_title, platform)
        caption = str(payload.get("caption") or "").strip() or self._fallback_caption(transcript_text, platform)
        hashtags_raw = payload.get("hashtags")
        hashtags = self._normalize_hashtags(hashtags_raw)
        if not hashtags:
            hashtags = self._fallback_hashtags(platform)

        title = title[: self.max_title_chars].strip() or self._fallback_title(base_title, platform)
        filename = self._build_filename(title=title, platform=platform, clip_index=clip_index)
        return PlatformMetadata(title=title, caption=caption, hashtags=hashtags, filename=filename)

    def _fallback_title(self, base_title: str, platform: str) -> str:
        stem = sanitize_filename(base_title, default="clip").replace("_", " ").strip()
        suffix = platform.upper()
        return f"{stem} | {suffix}"

    def _fallback_caption(self, transcript_text: str, platform: str) -> str:
        trimmed = " ".join(transcript_text.strip().split())
        preview = trimmed[:180].strip()
        if not preview:
            preview = "Auto generated clip."
        return f"{preview}\n\n#{platform} #autoclipper"

    def _normalize_hashtags(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        clean: list[str] = []
        for item in value:
            token = str(item).strip().replace(" ", "")
            if not token:
                continue
            if not token.startswith("#"):
                token = f"#{token}"
            token = sanitize_filename(token.replace("#", ""), default="clip")
            if token:
                clean.append(f"#{token.lower()}")
        return clean[:12]

    def _fallback_hashtags(self, platform: str) -> list[str]:
        return [f"#{platform}", "#shorts", "#autoclipper"]

    def _build_filename(self, *, title: str, platform: str, clip_index: int) -> str:
        safe_title = sanitize_filename(title, default="clip")
        safe_platform = sanitize_filename(platform, default="platform")
        return f"{clip_index:02d}_{safe_platform}_{safe_title}.mp4"
