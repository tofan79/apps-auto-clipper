from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev

from services.ai_engine.transcriber import WordTimestamp


@dataclass(slots=True)
class HookCandidate:
    start: float
    end: float
    viral_score: int
    emotion_score: float
    speech_spike: bool
    confidence: float
    reason: str


class ViralHookDetector:
    IMPACT_KEYWORDS = {
        "shocking",
        "secret",
        "mistake",
        "truth",
        "viral",
        "insane",
        "gila",
        "rahasia",
        "penting",
        "jangan",
    }

    def detect(
        self,
        *,
        words: list[WordTimestamp],
        llm_hooks: list[dict],
        max_clips: int = 10,
        min_viral_score: int = 60,
    ) -> list[HookCandidate]:
        if not llm_hooks:
            return []

        speed_windows = self._speech_speed_windows(words)
        keyword_windows = self._keyword_windows(words)

        candidates: list[HookCandidate] = []
        for hook in llm_hooks:
            start = float(hook.get("start", 0.0))
            end = float(hook.get("end", start))
            if end <= start:
                continue

            emotion_score = self._clamp01(float(hook.get("emotion_score", 0.5)))
            semantic_score = self._clamp01(float(hook.get("semantic_score", 0.5)))
            confidence = self._clamp01(float(hook.get("confidence", 0.7)))
            speed_spike = self._has_speech_spike(speed_windows, start, end)
            keyword_score = self._keyword_score_in_range(keyword_windows, start, end)

            viral_score = int(
                (0.30 * emotion_score + 0.25 * semantic_score + 0.25 * (1.0 if speed_spike else 0.0) + 0.20 * keyword_score)
                * 100
            )
            if viral_score < min_viral_score:
                continue

            candidates.append(
                HookCandidate(
                    start=start,
                    end=end,
                    viral_score=max(0, min(100, viral_score)),
                    emotion_score=emotion_score,
                    speech_spike=speed_spike,
                    confidence=confidence,
                    reason=str(hook.get("reason", "scored by multi-signal detector")),
                )
            )

        candidates.sort(key=lambda item: item.viral_score, reverse=True)
        return candidates[:max_clips]

    def _speech_speed_windows(self, words: list[WordTimestamp], window_sec: int = 5) -> list[tuple[float, float, float]]:
        if not words:
            return []
        start = min(item.start for item in words)
        end = max(item.end for item in words)

        windows: list[tuple[float, float, float]] = []
        cursor = start
        while cursor < end:
            window_end = min(end, cursor + window_sec)
            count = sum(1 for w in words if w.start >= cursor and w.start < window_end)
            duration = max(0.1, window_end - cursor)
            windows.append((cursor, window_end, count / duration))
            cursor += window_sec
        return windows

    def _keyword_windows(self, words: list[WordTimestamp], window_sec: int = 5) -> list[tuple[float, float, float]]:
        if not words:
            return []
        start = min(item.start for item in words)
        end = max(item.end for item in words)

        windows: list[tuple[float, float, float]] = []
        cursor = start
        while cursor < end:
            window_end = min(end, cursor + window_sec)
            window_words = [w for w in words if w.start >= cursor and w.start < window_end]
            if not window_words:
                windows.append((cursor, window_end, 0.0))
                cursor += window_sec
                continue
            hits = 0
            for item in window_words:
                token = item.word.lower().strip(".,!?\"'()[]{}")
                if token in self.IMPACT_KEYWORDS:
                    hits += 1
            windows.append((cursor, window_end, hits / len(window_words)))
            cursor += window_sec
        return windows

    def _has_speech_spike(self, windows: list[tuple[float, float, float]], start: float, end: float) -> bool:
        if not windows:
            return False
        rates = [rate for _, _, rate in windows]
        baseline = mean(rates)
        deviation = pstdev(rates) if len(rates) > 1 else 0.0
        threshold = baseline + max(0.2, deviation)
        target = [rate for w_start, w_end, rate in windows if w_start < end and w_end > start]
        return any(rate > threshold for rate in target)

    def _keyword_score_in_range(self, windows: list[tuple[float, float, float]], start: float, end: float) -> float:
        target = [score for w_start, w_end, score in windows if w_start < end and w_end > start]
        if not target:
            return 0.0
        return self._clamp01(mean(target))

    def _clamp01(self, value: float) -> float:
        return max(0.0, min(1.0, value))
