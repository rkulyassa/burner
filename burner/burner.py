import numpy as np
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Optional

from . import animations
from .globals import TMP_DIR
from .probe import Probe
from .typing import RawTranscript, SubtitleOptions, WhisperModel
from .utils import filter_alnum, measure
from .transcription import (
    load_subtitles_from_file,
    load_subtitles_from_raw_transcript,
    transcribe_video,
)


class Burner:
    def __init__(
        self,
        video_path: Path,
        transcript: Optional[Path | RawTranscript] = None,
        whisper_model: WhisperModel = "base",
    ) -> None:
        self.video_path = video_path

        if not TMP_DIR.exists():
            TMP_DIR.mkdir()

        if isinstance(transcript, Path):
            self.subtitles = load_subtitles_from_file(transcript)
        elif type(transcript) == RawTranscript:
            self.subtitles = load_subtitles_from_raw_transcript(transcript)
        else:
            self.subtitles = transcribe_video(video_path, whisper_model)

        self.probe = Probe(video_path)
        w, h = self.probe.size
        self.positions = {
            "top": (w / 2, h * 0.25),
            "middle": (w / 2, h / 2),
            "bottom": (w / 2, h * 0.75),
        }

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
            xy=self.positions[options.position],
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
            f"[1:v]setpts=PTS+{options.render_offset}/TB[v1];[0:v][v1]overlay=0:0",
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

        blank_frame_bytes = np.zeros(
            (self.probe.size[0], self.probe.size[1], 4), dtype=np.uint8
        ).tobytes()

        try:
            for n in range(self.probe.frame_count):
                subtitle_token = max(
                    (
                        token
                        for token in self.subtitles
                        if n >= round(token.start * self.probe.fps)
                    ),
                    key=lambda token: token.start,
                    default=None,
                )

                if subtitle_token:
                    text, start = subtitle_token
                    start_frame = round(start * self.probe.fps)
                    t = (n - start_frame) / self.probe.fps
                    img = self._get_text_image(
                        text, scale=animations.pop(t), options=options
                    )
                    img_bytes = np.array(img).tobytes()
                else:
                    img_bytes = blank_frame_bytes

                ffmpeg_process.stdin.write(img_bytes)
        finally:
            ffmpeg_process.stdin.close()
            ffmpeg_process.wait()
