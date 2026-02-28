from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass(slots=True)
class FaceBox:
    x: float
    y: float
    width: float
    height: float

    @property
    def center_x(self) -> float:
        return self.x + (self.width / 2.0)

    @property
    def center_y(self) -> float:
        return self.y + (self.height / 2.0)

    @property
    def area(self) -> float:
        return self.width * self.height


@dataclass(slots=True)
class FrameFaces:
    timestamp: float
    faces: list[FaceBox]


@dataclass(slots=True)
class SegmentDecision:
    start: float
    end: float
    mode: str
    crop_center_x: float
    crop_center_y: float
    face_count: int


class FaceAnalyzer:
    """
    Analyze per-frame face samples and produce deterministic segment decisions
    for adaptive portrait/landscape rendering.
    """

    def __init__(
        self,
        *,
        segment_duration_sec: float = 2.0,
        min_switch_duration_sec: float = 1.2,
        crop_damping: float = 0.65,
    ) -> None:
        self.segment_duration_sec = max(0.25, segment_duration_sec)
        self.min_switch_duration_sec = max(0.25, min_switch_duration_sec)
        self.crop_damping = max(0.0, min(0.95, crop_damping))

    def analyze(
        self,
        *,
        frame_samples: list[FrameFaces],
        clip_start: float,
        clip_end: float,
    ) -> list[SegmentDecision]:
        if clip_end <= clip_start:
            raise ValueError("clip_end must be greater than clip_start")

        segments = self._segment_range(clip_start, clip_end)
        decisions = [self._analyze_window(frame_samples=frame_samples, start=start, end=end) for start, end in segments]
        merged = self.merge_adjacent_segments(decisions)
        stable = self.apply_anti_flicker(merged)
        return self.smooth_crop_centers(stable)

    def merge_adjacent_segments(self, segments: list[SegmentDecision]) -> list[SegmentDecision]:
        if not segments:
            return []
        merged: list[SegmentDecision] = [segments[0]]
        for current in segments[1:]:
            prev = merged[-1]
            if current.mode != prev.mode:
                merged.append(current)
                continue
            duration_a = max(0.01, prev.end - prev.start)
            duration_b = max(0.01, current.end - current.start)
            combined = duration_a + duration_b
            merged[-1] = SegmentDecision(
                start=prev.start,
                end=current.end,
                mode=prev.mode,
                crop_center_x=((prev.crop_center_x * duration_a) + (current.crop_center_x * duration_b)) / combined,
                crop_center_y=((prev.crop_center_y * duration_a) + (current.crop_center_y * duration_b)) / combined,
                face_count=round(((prev.face_count * duration_a) + (current.face_count * duration_b)) / combined),
            )
        return merged

    def apply_anti_flicker(self, segments: list[SegmentDecision]) -> list[SegmentDecision]:
        if len(segments) <= 2:
            return segments
        stabilized: list[SegmentDecision] = []
        for index, segment in enumerate(segments):
            if index == 0 or index == len(segments) - 1:
                stabilized.append(segment)
                continue
            duration = segment.end - segment.start
            prev_mode = segments[index - 1].mode
            next_mode = segments[index + 1].mode
            if duration < self.min_switch_duration_sec and prev_mode == next_mode:
                replacement = SegmentDecision(
                    start=segment.start,
                    end=segment.end,
                    mode=prev_mode,
                    crop_center_x=(segments[index - 1].crop_center_x + segments[index + 1].crop_center_x) / 2.0,
                    crop_center_y=(segments[index - 1].crop_center_y + segments[index + 1].crop_center_y) / 2.0,
                    face_count=round((segments[index - 1].face_count + segments[index + 1].face_count) / 2.0),
                )
                stabilized.append(replacement)
            else:
                stabilized.append(segment)
        return self.merge_adjacent_segments(stabilized)

    def smooth_crop_centers(self, segments: list[SegmentDecision]) -> list[SegmentDecision]:
        if not segments:
            return []
        smoothed: list[SegmentDecision] = []
        prev_x = segments[0].crop_center_x
        prev_y = segments[0].crop_center_y
        for segment in segments:
            next_x = (self.crop_damping * prev_x) + ((1.0 - self.crop_damping) * segment.crop_center_x)
            next_y = (self.crop_damping * prev_y) + ((1.0 - self.crop_damping) * segment.crop_center_y)
            smoothed_segment = SegmentDecision(
                start=segment.start,
                end=segment.end,
                mode=segment.mode,
                crop_center_x=self._clamp01(next_x),
                crop_center_y=self._clamp01(next_y),
                face_count=segment.face_count,
            )
            smoothed.append(smoothed_segment)
            prev_x, prev_y = smoothed_segment.crop_center_x, smoothed_segment.crop_center_y
        return smoothed

    def _segment_range(self, start: float, end: float) -> list[tuple[float, float]]:
        segments: list[tuple[float, float]] = []
        cursor = start
        while cursor < end:
            next_edge = min(end, cursor + self.segment_duration_sec)
            segments.append((cursor, next_edge))
            cursor = next_edge
        return segments

    def _analyze_window(self, *, frame_samples: list[FrameFaces], start: float, end: float) -> SegmentDecision:
        window = [item for item in frame_samples if item.timestamp >= start and item.timestamp < end]
        if not window:
            return SegmentDecision(
                start=start,
                end=end,
                mode="landscape_blur",
                crop_center_x=0.5,
                crop_center_y=0.5,
                face_count=0,
            )

        non_empty = [item for item in window if item.faces]
        if not non_empty:
            return SegmentDecision(
                start=start,
                end=end,
                mode="landscape_blur",
                crop_center_x=0.5,
                crop_center_y=0.5,
                face_count=0,
            )

        face_counts = [len(item.faces) for item in non_empty]
        primary_faces = [max(item.faces, key=lambda face: face.area) for item in non_empty]
        avg_count = mean(face_counts)
        avg_area = mean(face.area for face in primary_faces)
        center_x = mean(face.center_x for face in primary_faces)
        center_y = mean(face.center_y for face in primary_faces)

        if avg_count >= 1.5:
            mode = "landscape_blur"
        elif avg_area >= 0.02:
            mode = "portrait"
        else:
            mode = "landscape_blur"

        return SegmentDecision(
            start=start,
            end=end,
            mode=mode,
            crop_center_x=self._clamp01(center_x),
            crop_center_y=self._clamp01(center_y),
            face_count=round(avg_count),
        )

    def _clamp01(self, value: float) -> float:
        return max(0.0, min(1.0, value))
