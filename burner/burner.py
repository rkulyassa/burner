import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

from . import animations
from .probe import Probe
from ._typing import RawTranscript, SubtitleOptions, PathLike, WhisperModel
from ._utils import filter_alnum, measure
from .transcription import (
    load_transcript_from_file,
    load_transcript_from_raw_transcript,
    transcribe,
)


class Burner:
    def __init__(
        self,
        video_path: PathLike,
        transcript: Optional[PathLike | RawTranscript] = None,
        whisper_model: WhisperModel = "base",
    ) -> None:
        self.video_path = video_path

        if isinstance(transcript, PathLike):
            self.transcript = load_transcript_from_file(transcript)
        elif type(transcript) == RawTranscript:
            self.transcript = load_transcript_from_raw_transcript(transcript)
        else:
            self.transcript = transcribe(video_path, whisper_model)

        self.probe = Probe(video_path)

    def __enter__(self) -> "Burner":
        return self

    def __exit__(self, *args: object) -> None:
        return

    def _get_text_image(
        self, text: str, scale: float, options: SubtitleOptions
    ) -> Image.Image:
        if options.filter_alnum:
            text = filter_alnum(text)
        if options.capitalize:
            text = text.upper()
        image = Image.new(mode="RGBA", size=self.probe.size)
        draw = ImageDraw.Draw(image)
        font_size = int(options.font_size * scale)
        font = ImageFont.truetype(options.font_path, font_size)
        draw.text(
            xy=self.probe.center,
            text=text,
            fill=options.font_fill,
            font=font,
            anchor="mm",
            language="en",
            stroke_width=options.stroke_width,
            stroke_fill=options.stroke_fill,
        )
        return image

    def burn(
        self, out_path: str = "out.mp4", options: SubtitleOptions = SubtitleOptions()
    ) -> None:  # @TODO: add animation parameter

        ffmpeg_command = [
            "ffmpeg",
            "-i",
            str(self.video_path),
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgba",
            "-s",
            f"1080x1920",
            "-framerate",
            str(self.probe.fps),
            "-i",
            "-",
            "-filter_complex",
            f"[1:v]setpts=PTS+{self.transcript.offset}[v1];[0:v][v1]overlay=0:0",
            "-map",
            "0:a",
            "-c:v",
            "libx264",
            "-c:a",
            "copy",
            "-loglevel",
            "error",
            out_path,
        ]

        ffmpeg_process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

        try:
            for n in range(self.probe.frame_count):
                for text, start, end in self.transcript.subtitles:
                    start_frame = round(start * self.probe.fps)
                    end_frame = round(end * self.probe.fps)
                    if n < start_frame or n > end_frame:
                        continue
                    t = (n - start_frame) / self.probe.fps
                    img = self._get_text_image(
                        text, scale=animations.pop(t), options=options
                    )
                    img_bytes = np.array(img).tobytes()
                    ffmpeg_process.stdin.write(img_bytes)
        finally:
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
