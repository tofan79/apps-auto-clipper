from __future__ import annotations

import json
from dataclasses import dataclass
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
class OllamaProvider(BaseLLMProvider):
    model: str
    base_url: str = "http://127.0.0.1:11434"

    def health_check(self) -> bool:
        try:
            import httpx  # type: ignore
        except Exception:
            return False
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def generate_hooks(self, transcript_text: str, *, max_candidates: int = 15) -> list[dict[str, Any]]:
        prompt = (
            "Analyze transcript and return ONLY JSON array of hook candidates. "
            f"Need up to {max_candidates} items with keys: start,end,semantic_score,emotion_score,reason,confidence.\n\n"
            f"Transcript:\n{transcript_text}"
        )
        payload = self._generate(prompt)
        parsed = _extract_json_payload(payload)
        if isinstance(parsed, list):
            return [item for item in parsed if isinstance(item, dict)][:max_candidates]
        return []

    def generate_metadata(self, transcript_text: str, *, platform: str) -> dict[str, Any]:
        prompt = (
            f"Create short-form {platform} metadata. Return JSON object with keys: title,caption,hashtags.\n\n"
            f"Transcript:\n{transcript_text}"
        )
        payload = self._generate(prompt)
        parsed = _extract_json_payload(payload)
        if isinstance(parsed, dict):
            return parsed
        return {"title": "", "caption": "", "hashtags": []}

    def _generate(self, prompt: str) -> str:
        try:
            import httpx  # type: ignore
        except Exception as exc:
            raise RuntimeError("httpx is required for Ollama provider") from exc

        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload.get("response", "")).strip()
