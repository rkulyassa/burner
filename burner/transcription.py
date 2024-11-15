import json
import subprocess
from pathlib import Path
from sys import platform

from .globals import TMP_DIR
from .typing import RawTranscript, SubtitleToken, WhisperModel
from .utils import measure


def load_subtitles_from_raw_transcript(
    raw_transcript: RawTranscript,
) -> list[SubtitleToken]:
    word_segments = raw_transcript["word_segments"]
    subtitle_tokens = []
    for word_segment in word_segments:
        text = word_segment["word"]
        start = word_segment["start"]
        subtitle_token = SubtitleToken(text, start)
        subtitle_tokens.append(subtitle_token)
    return subtitle_tokens


def load_subtitles_from_file(transcript_path: Path) -> list[SubtitleToken]:
    with open(transcript_path) as f:
        raw_transcript: RawTranscript = json.load(f)
    subtitles = load_subtitles_from_raw_transcript(raw_transcript)
    return subtitles


def _extract_audio(video_file: Path) -> Path:
    out_path = TMP_DIR.joinpath("audio.wav")
    command = [
        "ffmpeg",
        "-i",
        str(video_file),
        "-q:a",
        "0",
        "-map",
        "a",
        "-loglevel",
        "error",
        "-y",
        str(out_path),
    ]
    subprocess.run(command, check=True)
    return out_path


def transcribe_audio(
    audio_path: Path,
    model_name: WhisperModel,
    language: str = "en",
) -> list[SubtitleToken]:
    compute_type = "int8" if platform == "darwin" else "float16"

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
        str(audio_path),
    ]

    subprocess.run(whisperx_command, cwd=TMP_DIR, check=True)

    transcript_path = audio_path.with_suffix(".json")
    subtitles = load_subtitles_from_file(transcript_path)
    return subtitles


def transcribe_video(
    video_path: Path, model_name: WhisperModel, language: str = "en"
) -> list[SubtitleToken]:
    audio_path = _extract_audio(video_path)
    subtitles = transcribe_audio(audio_path, model_name, language)
    return subtitles
