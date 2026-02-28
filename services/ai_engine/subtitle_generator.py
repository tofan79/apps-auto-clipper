from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from services.ai_engine.transcriber import WordTimestamp


@dataclass(slots=True)
class SubtitleStyle:
    name: str
    font_name: str
    font_size: int
    primary_colour: str
    secondary_colour: str
    outline_colour: str
    back_colour: str
    bold: int
    italic: int
    alignment: int
    margin_v: int


DEFAULT_STYLE = SubtitleStyle(
    name="Karaoke",
    font_name="Arial",
    font_size=64,
    primary_colour="&H00FFFFFF",
    secondary_colour="&H0000FFFF",
    outline_colour="&H00000000",
    back_colour="&H64000000",
    bold=1,
    italic=0,
    alignment=2,
    margin_v=90,
)


class SubtitleGenerator:
    def __init__(self, style: SubtitleStyle | None = None) -> None:
        self.style = style or DEFAULT_STYLE

    def generate_ass(self, *, words: list[WordTimestamp], output_path: Path, group_size: int = 4) -> Path:
        if not words:
            raise ValueError("words cannot be empty for subtitle generation")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        normalized = sorted(words, key=lambda item: item.start)
        events = self._build_events(normalized, group_size=max(1, group_size))
        body = self._build_ass_document(events)
        output_path.write_text(body, encoding="utf-8")
        return output_path

    def _build_events(self, words: list[WordTimestamp], group_size: int) -> list[str]:
        events: list[str] = []
        for index in range(0, len(words), group_size):
            group = words[index : index + group_size]
            start = group[0].start
            end = group[-1].end
            karaoke_text_parts: list[str] = []
            for item in group:
                duration_cs = max(1, int(round((item.end - item.start) * 100)))
                karaoke_text_parts.append(f"{{\\k{duration_cs}}}{item.word}")
            text = " ".join(karaoke_text_parts)
            event = (
                f"Dialogue: 0,{self._format_ass_time(start)},{self._format_ass_time(end)},"
                f"{self.style.name},,0,0,0,,{text}"
            )
            events.append(event)
        return events

    def _build_ass_document(self, events: list[str]) -> str:
        style = self.style
        header = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "Collisions: Normal",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: "
            f"{style.name},{style.font_name},{style.font_size},{style.primary_colour},{style.secondary_colour},"
            f"{style.outline_colour},{style.back_colour},{style.bold},{style.italic},0,0,100,100,0,0,1,2,1,"
            f"{style.alignment},40,40,{style.margin_v},1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        ]
        return "\n".join(header + events) + "\n"

    def _format_ass_time(self, value: float) -> str:
        total_cs = max(0, int(round(value * 100)))
        centiseconds = total_cs % 100
        total_seconds = total_cs // 100
        seconds = total_seconds % 60
        total_minutes = total_seconds // 60
        minutes = total_minutes % 60
        hours = total_minutes // 60
        return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"
