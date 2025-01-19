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
        highlight = word_segment["highlight"] if "highlight" in word_segment else 0 # checks for highlight in case whisper doesn't generate any
        subtitle_token = SubtitleToken(text, start, highlight)
        subtitle_tokens.append(subtitle_token)
    return subtitle_tokens


def load_subtitles_from_file(transcript_path: Path) -> list[SubtitleToken]:
    with open(transcript_path) as f:
        raw_transcript: RawTranscript = json.load(f)
    subtitles = load_subtitles_from_raw_transcript(raw_transcript)
    return subtitles


def _extract_audio(
    video_file: Path,
) -> (
    Path
):  # TODO: dynamically handle audio codec based on probe. only supports aac for now
    out_path = TMP_DIR.joinpath("audio.aac")
    command = [
        "ffmpeg",
        "-i",
        str(video_file),
        "-vn",
        "-acodec",
        "copy",
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
    cpu: bool = False
) -> list[SubtitleToken]:
    compute_type = "int8" if platform == "darwin" else "float16"

    whisperx_command = [
        "whisperx",
        "--model",
        model_name,
        "--compute_type",
        compute_type if not cpu else "int8",
        "--output_format",
        "json",
        "--suppress_numerals",
        "--task",
        "transcribe",
        "--language",
        language,
        "--device",
        "cpu" if cpu else "cuda",
        str(audio_path),
    ]
    subprocess.run(whisperx_command, cwd=TMP_DIR, check=True)

    transcript_path = audio_path.with_suffix(".json")
    subtitles = load_subtitles_from_file(transcript_path)
    return subtitles


def transcribe_video(
    video_file: Path, model_name: WhisperModel, language: str = "en", cpu: bool = False
) -> list[SubtitleToken]:
    audio_path = _extract_audio(video_file)
    subtitles = transcribe_audio(audio_path, model_name, language, cpu)
    return subtitles
