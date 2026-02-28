from __future__ import annotations

from services.ai_engine.hook_detector import ViralHookDetector
from services.ai_engine.transcriber import WordTimestamp


def _build_words() -> list[WordTimestamp]:
    words: list[WordTimestamp] = []
    for index in range(5):
        start = 1.0 + index * 1.0
        words.append(WordTimestamp(word="normal", start=start, end=start + 0.2, probability=0.9))

    for index in range(20):
        start = 10.0 + index * 0.2
        token = "rahasia" if index % 4 == 0 else "fast"
        words.append(WordTimestamp(word=token, start=start, end=start + 0.15, probability=0.9))
    return words


def test_detect_returns_sorted_candidates() -> None:
    detector = ViralHookDetector()
    llm_hooks = [
        {
            "start": 10.0,
            "end": 14.0,
            "semantic_score": 0.9,
            "emotion_score": 0.8,
            "confidence": 0.9,
            "reason": "hook burst",
        },
        {
            "start": 1.0,
            "end": 3.0,
            "semantic_score": 0.5,
            "emotion_score": 0.4,
            "confidence": 0.7,
            "reason": "slow intro",
        },
    ]
    items = detector.detect(words=_build_words(), llm_hooks=llm_hooks, min_viral_score=0, max_clips=10)
    assert len(items) == 2
    assert items[0].viral_score >= items[1].viral_score
    assert 0 <= items[0].viral_score <= 100
    assert items[0].speech_spike is True
