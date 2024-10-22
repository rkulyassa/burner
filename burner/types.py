from typing import TypedDict, List


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


class Transcript(TypedDict):
    segments: List[Segment]
    word_segments: List[WordSegment]
