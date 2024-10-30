import json
import os
import subprocess
from pathlib import Path
from shutil import rmtree
from sys import platform
from typing import List

from ._typing import RawTranscript, SubtitleToken, PathLike, WhisperModel
from ._utils import measure

TMP_DIR = Path(__file__).parent.joinpath("tmp")


def load_subtitles_from_raw_transcript(
    raw_transcript: RawTranscript,
) -> List[SubtitleToken]:
    word_segments = raw_transcript["word_segments"]
    subtitle_tokens = []
    for word_segment in word_segments:
        text = word_segment["word"]
        start = word_segment["start"]
        subtitle_token = SubtitleToken(text, start)
        subtitle_tokens.append(subtitle_token)
    return subtitle_tokens


def load_subtitles_from_file(transcript_path: PathLike) -> List[SubtitleToken]:
    with open(transcript_path) as f:
        raw_transcript: RawTranscript = json.load(f)
    subtitles = load_subtitles_from_raw_transcript(raw_transcript)
    return subtitles


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
    model_name: WhisperModel,
    language: str = "en",
) -> List[SubtitleToken]:
    if os.path.exists(TMP_DIR):
        rmtree(TMP_DIR)
    os.makedirs(TMP_DIR)

    compute_type = "int8" if platform == "darwin" else "float16"
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
    subtitles = load_subtitles_from_file(transcript_path)
    rmtree(TMP_DIR)
    return subtitles
