from __future__ import annotations

from services.ai_engine.face_analyzer import FaceAnalyzer, FaceBox, FrameFaces, SegmentDecision


def test_face_analyzer_prefers_portrait_for_single_face() -> None:
    analyzer = FaceAnalyzer(segment_duration_sec=2.0, min_switch_duration_sec=1.0)
    frames = [
        FrameFaces(timestamp=0.1, faces=[FaceBox(x=0.42, y=0.2, width=0.24, height=0.36)]),
        FrameFaces(timestamp=1.2, faces=[FaceBox(x=0.40, y=0.22, width=0.23, height=0.35)]),
        FrameFaces(timestamp=2.1, faces=[FaceBox(x=0.44, y=0.18, width=0.25, height=0.34)]),
        FrameFaces(timestamp=3.4, faces=[FaceBox(x=0.45, y=0.20, width=0.26, height=0.34)]),
    ]
    segments = analyzer.analyze(frame_samples=frames, clip_start=0.0, clip_end=4.0)
    assert segments
    assert all(item.mode == "portrait" for item in segments)


def test_face_analyzer_prefers_landscape_for_two_faces() -> None:
    analyzer = FaceAnalyzer(segment_duration_sec=2.0, min_switch_duration_sec=1.0)
    frames = [
        FrameFaces(
            timestamp=0.5,
            faces=[
                FaceBox(x=0.20, y=0.20, width=0.20, height=0.30),
                FaceBox(x=0.60, y=0.18, width=0.22, height=0.32),
            ],
        ),
        FrameFaces(
            timestamp=1.5,
            faces=[
                FaceBox(x=0.21, y=0.22, width=0.20, height=0.31),
                FaceBox(x=0.58, y=0.19, width=0.23, height=0.30),
            ],
        ),
    ]
    segments = analyzer.analyze(frame_samples=frames, clip_start=0.0, clip_end=2.0)
    assert len(segments) == 1
    assert segments[0].mode == "landscape_blur"


def test_face_analyzer_anti_flicker_merges_short_switches() -> None:
    analyzer = FaceAnalyzer(segment_duration_sec=2.0, min_switch_duration_sec=1.5)
    segments = [
        SegmentDecision(0.0, 3.0, "portrait", 0.40, 0.40, 1),
        SegmentDecision(3.0, 3.8, "landscape_blur", 0.50, 0.50, 2),
        SegmentDecision(3.8, 8.0, "portrait", 0.60, 0.60, 1),
    ]
    stabilized = analyzer.apply_anti_flicker(segments)
    assert len(stabilized) == 1
    assert stabilized[0].mode == "portrait"
    assert stabilized[0].start == 0.0
    assert stabilized[0].end == 8.0
