import numpy as np
import subprocess
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

from . import animations
from ._typing import PathLike, RawTranscript, SubtitleOptions
from ._utils import measure
from .transcription import load_transcript, parse_transcript, transcribe


def _filter_alnum(input: str) -> str:
    return "".join([c if c.isalnum() else " " if c == "-" else "" for c in input])


class Burner:
    def __init__(
        self,
        video_path: PathLike,
        transcript: Optional[PathLike | RawTranscript] = None,
        # @TODO: determine with ffprobe
        fps: int = 60,
        video_size: Tuple[int, int] = (1080, 1920),
    ) -> None:
        self.video_path = video_path

        if type(transcript) == PathLike:
            self.transcript = load_transcript(transcript)
        elif type(transcript) == RawTranscript:
            self.transcript = parse_transcript(transcript)
        else:
            self.transcript = transcribe(video_path, compute_type="int8")

        self.fps = fps
        self.video_size = video_size

    def __enter__(self) -> "Burner":
        return self

    def __exit__(self, *args: object) -> None:
        return

    def _get_center(self) -> Tuple[float, float]:
        w, h = self.video_size
        return (w / 2, h / 2)

    def _get_text_image(
        self, text: str, scale: float, options: SubtitleOptions
    ) -> Image.Image:
        if options.filter_alnum:
            text = _filter_alnum(text)
        if options.capitalize:
            text = text.upper()
        image = Image.new(mode="RGBA", size=self.video_size)
        draw = ImageDraw.Draw(image)
        # scaled_font = options.font.font_variant(size=int(options.font.size * scale))
        font_size = int(options.font_size * scale)
        font = ImageFont.truetype(options.font_path, font_size)
        draw.text(
            xy=self._get_center(),
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
            str(self.fps),
            "-i",
            "-",
            "-filter_complex",
            "[0:v][1:v] overlay=0:0",
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

        process = subprocess.Popen(ffmpeg_command, stdin=subprocess.PIPE)

        try:
            for text, duration in self.transcript:
                n = int(duration * self.fps)
                for i in range(n):
                    t = i / self.fps
                    img = self._get_text_image(
                        text, scale=animations.pop(t), options=options
                    )
                    img_bytes = np.array(img).tobytes()
                    process.stdin.write(img_bytes)
        finally:
            process.stdin.close()
            process.wait()
