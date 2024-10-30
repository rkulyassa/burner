import os

from typing import List, NamedTuple, Tuple, TypedDict, Union


PathLike = Union[str, bytes, os.PathLike]


class SubtitleOptions(NamedTuple):
    font_path: PathLike = "fonts/Montserrat-Black.ttf"
    font_size: float = 90.0
    font_fill: Tuple[int, int, int] = (255, 255, 255)
    stroke_width: int = 8
    stroke_fill: Tuple[int, int, int] = (0, 0, 0)
    render_offset: float = 0.0
    filter_alnum: bool = True
    capitalize: bool = True


class SubtitleToken(NamedTuple):
    text: str
    duration: float


class WordSegment(TypedDict):
    word: str
    start: float
    end: float
    score: float


class Segment(TypedDict):
    start: float
    end: float
    text: str
    words: List[WordSegment]


class RawTranscript(TypedDict):
    segments: List[Segment]
    word_segments: List[WordSegment]