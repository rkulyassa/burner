import json
import os
import subprocess
from pathlib import Path
from shutil import rmtree
from sys import platform
from typing import List

from ._globals import TMP_DIR
from ._typing import RawTranscript, SubtitleToken, Transcript, PathLike, WhisperModel
from ._utils import measure


def _parse_subtitles(
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
        subtitle_token = SubtitleToken(text, start, end)
        subtitle_tokens.append(subtitle_token)
    return subtitle_tokens


def load_transcript_from_raw_transcript(raw_transcript: RawTranscript) -> Transcript:
    offset = raw_transcript["word_segments"][0]["start"]
    subtitles = _parse_subtitles(raw_transcript)
    transcript = Transcript(offset, subtitles)
    return transcript


def load_transcript_from_file(transcript_path: PathLike) -> Transcript:
    with open(transcript_path) as f:
        raw_transcript: RawTranscript = json.load(f)
    transcript = load_transcript_from_raw_transcript(raw_transcript)
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
    model_name: WhisperModel,
    language: str = "en",
) -> Transcript:
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
    transcript = load_transcript_from_file(transcript_path)
    rmtree(TMP_DIR)
    return transcript
