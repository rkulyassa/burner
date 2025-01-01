from pathlib import Path
from typing import Literal, NamedTuple, Tuple, TypedDict

from .globals import ROOT_DIR

WhisperModel = Literal[
    "tiny.en",
    "tiny",
    "base.en",
    "base",
    "small.en",
    "small",
    "medium.en",
    "medium",
    "large",
    "large-v2",
]


class SubtitleOptions(NamedTuple):
    position: Literal["top", "middle", "bottom"] = "middle"
    font_path: Path = ROOT_DIR / "fonts" / "Anton-Regular.ttf"
    font_size: float = 60.0
    font_fill: Tuple[int, int, int] = (255, 255, 255)
    stroke_width: int = 4
    stroke_fill: Tuple[int, int, int] = (0, 0, 0)
    render_offset: float = 0.0
    filter_chars: bool = True
    capitalize: bool = True


class SubtitleToken(NamedTuple):
    text: str
    start: float


class WordSegment(TypedDict):
    word: str
    start: float
    end: float
    score: float


class Segment(TypedDict):
    start: float
    end: float
    text: str
    words: list[WordSegment]


class RawTranscript(TypedDict):
    segments: list[Segment]
    word_segments: list[WordSegment]
