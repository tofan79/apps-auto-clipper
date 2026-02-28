from __future__ import annotations

from services.ai_engine.metadata_generator import PlatformMetadataGenerator
from services.ai_engine.providers.base import BaseLLMProvider


class _FakeProvider(BaseLLMProvider):
    def health_check(self) -> bool:
        return True

    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict]:
        return []

    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict:
        return {
            "title": f"{platform.title()} Viral Clip",
            "caption": f"{platform} caption",
            "hashtags": [platform, "Shorts", "AutoClipper"],
        }


class _BrokenProvider(BaseLLMProvider):
    def health_check(self) -> bool:
        return False

    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict]:
        return []

    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict:
        raise RuntimeError("upstream down")


def test_generate_metadata_for_all_platforms_from_provider() -> None:
    generator = PlatformMetadataGenerator()
    payload = generator.generate_for_platforms(
        transcript_text="this is transcript text",
        base_title="My Source Title",
        provider=_FakeProvider(),
        clip_index=2,
    )
    assert set(payload.keys()) == {"youtube", "tiktok", "instagram", "facebook"}
    assert payload["youtube"].title == "Youtube Viral Clip"
    assert payload["youtube"].filename.startswith("02_youtube_")
    assert payload["youtube"].hashtags[0] == "#youtube"


def test_generate_metadata_falls_back_when_provider_fails() -> None:
    generator = PlatformMetadataGenerator()
    payload = generator.generate_for_platforms(
        transcript_text="fallback transcript",
        base_title="Source/Unsafe:*Name",
        provider=_BrokenProvider(),
        clip_index=1,
    )
    assert payload["tiktok"].title
    assert payload["tiktok"].caption
    assert payload["tiktok"].hashtags
    assert payload["tiktok"].filename.endswith(".mp4")
