from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from services.ai_engine.providers.base import BaseLLMProvider


def _extract_json_payload(raw_text: str) -> Any:
    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("Provider returned empty response")

    if raw_text.startswith("```"):
        stripped = raw_text.strip("`")
        lines = stripped.splitlines()
        if lines and lines[0].lower().startswith("json"):
            lines = lines[1:]
        raw_text = "\n".join(lines).strip()

    start = raw_text.find("[")
    end = raw_text.rfind("]")
    if start != -1 and end != -1 and end >= start:
        return json.loads(raw_text[start : end + 1])

    start_obj = raw_text.find("{")
    end_obj = raw_text.rfind("}")
    if start_obj != -1 and end_obj != -1 and end_obj >= start_obj:
        return json.loads(raw_text[start_obj : end_obj + 1])
    return json.loads(raw_text)


@dataclass(slots=True)
class OpenRouterProvider(BaseLLMProvider):
    model: str
    api_key: str = field(repr=False)
    base_url: str = "https://openrouter.ai/api/v1"

    def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            import httpx  # type: ignore
        except Exception:
            return False
        try:
            response = httpx.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=8,
            )
            return response.status_code == 200
        except Exception:
            return False

    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict[str, Any]]:
        prompt = (
            "Analyze transcript and return ONLY JSON array of hook candidates with keys: "
            "start,end,semantic_score,emotion_score,reason,confidence.\n\n"
            f"Limit: {max_candidates} items.\n\nTranscript:\n{transcript_text}"
        )
        text = self._chat(prompt)
        parsed = _extract_json_payload(text)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)][:max_candidates]
        return []

    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict[str, Any]:
        prompt = (
            f"Create JSON object metadata for {platform} with keys title, caption, hashtags.\n\n"
            f"Transcript:\n{transcript_text}"
        )
        text = self._chat(prompt)
        parsed = _extract_json_payload(text)
        if isinstance(parsed, dict):
            return parsed
        return {"title": "", "caption": "", "hashtags": []}

    def _chat(self, prompt: str) -> str:
        try:
            import httpx  # type: ignore
        except Exception as exc:
            raise RuntimeError("httpx is required for OpenRouter provider") from exc

        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/tofan79/apps-auto-clipper",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.2,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices", [])
        if not choices:
            return ""
        message = choices[0].get("message", {})
        return str(message.get("content", "")).strip()
