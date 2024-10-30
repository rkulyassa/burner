import json
import os
import subprocess
from pathlib import Path
from shutil import rmtree
from typing import List

from ._globals import TMP_DIR
from ._typing import WordSegment, RawTranscript, SubtitleToken, PathLike
from ._utils import measure


def parse_transcript(
    raw_transcript: RawTranscript,
) -> List[SubtitleToken]:
    word_segments = raw_transcript["word_segments"]
    subtitle_tokens = []
    for i, word_segment in enumerate(word_segments):
        text = word_segment["word"]
        start = word_segment["start"]
        if i < len(word_segments) - 1:
            end = word_segments[i + 1]["start"]
        else:
            end = word_segment["end"]
        duration = end - start
        subtitle_token = SubtitleToken(text, duration)
        subtitle_tokens.append(subtitle_token)
    return subtitle_tokens


def load_transcript(transcript_path: PathLike) -> List[SubtitleToken]:
    with open(transcript_path) as f:
        raw_transcript: RawTranscript = json.load(f)
    transcript = parse_transcript(raw_transcript)
    return transcript


def _extract_audio(video_file: PathLike) -> Path:
    out_path = TMP_DIR.joinpath("audio.wav")
    command = [
        "ffmpeg",
        "-i",
        video_file,
        "-q:a",
        "0",
        "-map",
        "a",
        "-loglevel",
        "error",
        out_path,
    ]
    subprocess.run(command, check=True)
    return out_path


def transcribe(
    video_path: PathLike,
    model_name: str = "base",
    # device: str = "cuda",
    compute_type: str = "float16",
    language: str = "en",
) -> List[WordSegment]:
    if os.path.exists(TMP_DIR):
        rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    audio_path = _extract_audio(video_path)
    whisperx_command = [
        "whisperx",
        "--model",
        model_name,
        "--compute_type",
        compute_type,
        "--output_format",
        "json",
        "--suppress_numerals",
        "--task",
        "transcribe",
        "--language",
        language,
        audio_path,
    ]
    subprocess.run(whisperx_command, cwd=TMP_DIR, check=True)

    transcript_path = audio_path.with_suffix(".json")
    transcript = load_transcript(transcript_path)
    rmtree(TMP_DIR)
    return transcript
