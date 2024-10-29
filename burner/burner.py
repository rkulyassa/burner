from PIL import Image, ImageFont, ImageDraw, ImageColor
from moviepy.editor import (
    ImageSequenceClip,
    VideoClip,
    VideoFileClip,
    CompositeVideoClip,
)
from typing import Tuple, Union, Dict, List
from .animations import pop_up
from .types import Transcript, WordSegment
from .utils import filter_alnum
from .measure import measure
import numpy as np
import json
import time
import subprocess


class Burner:
    def __init__(
        self,
        base_video: str,
        transcript: Union[str, Transcript],
        font_path: str,
        font_size: float,
        fill: Tuple[int, int, int],
        stroke_width: float,
        stroke_fill: Tuple[int, int, int],
        fps: int = 60,
        size: Tuple[int, int] = (1080, 1920),
        render_offset: float = 0.0,
        filter_alnum: bool = True,
        capitalize: bool = True,
    ):
        self.base_video = base_video

        if type(transcript) == str:
            self.transcript = self._load_transcript(transcript)
        elif type(transcript) == Transcript:
            self.transcript = transcript
        else:
            self.transcript = transcript
            # raise TypeError()

        self.font = ImageFont.truetype(font_path, font_size)
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill
        self.fps = fps
        self.size = size
        self.render_offset = render_offset
        self.filter_alnum = filter_alnum
        self.capitalize = capitalize

    def _load_transcript(self, transcript_path: str) -> Transcript:
        with open(transcript_path) as f:
            transcript_data = json.load(f)
        return transcript_data

    def _get_center(self) -> Tuple[float, float]:
        w, h = self.size
        return (w / 2, h / 2)

    def get_text_image(self, text: str, scale: float) -> Image.Image:
        if self.filter_alnum:
            text = filter_alnum(text)
        if self.capitalize:
            text = text.upper()
        img = Image.new(mode="RGBA", size=self.size)
        draw = ImageDraw.Draw(img)
        scaled_font = self.font.font_variant(size=int(self.font.size * scale))
        draw.text(
            xy=self._get_center(),
            text=text,
            fill=self.fill,
            font=scaled_font,
            anchor="mm",
            language="en",
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_fill,
        )
        return img

    # def get_text_clip(
    #     self, text: str, start: float, end: float, fps: int = 60
    # ) -> ImageSequenceClip:
    #     duration = end - start
    #     img = self.get_text_img(text)
    #     w_i, h_i = img.size
    #     frames = []
    #     n = int(duration * fps)
    #     for i in range(n):
    #         t = i / fps
    #         scale = pop_up(t)
    #         w = int(w_i * scale)
    #         h = int(h_i * scale)
    #         container_img = img.copy()
    #         text_img = img.resize((w, h))
    #         offset = ((w_i - w) // 2, (h_i - h) // 2)
    #         container_img.paste(text_img, offset)
    #         frames.append(np.array(container_img))
    #     clip = ImageSequenceClip(frames, fps=fps)
    #     clip: ImageSequenceClip = clip.set_start(start)
    #     clip = clip.set_duration(duration)
    #     return clip

    # def get_subtitle_clip(self):
    #     clips = []
    #     word_segments = self.transcript["word_segments"]
    #     for i, word_segment in enumerate(word_segments):
    #         text = word_segment["word"]
    #         start = word_segment["start"]
    #         if i < len(word_segments) - 1:
    #             end = word_segments[i + 1]["start"]
    #         else:
    #             end = word_segment["end"]
    #         clip = self.get_text_clip(text, start, end)
    #         clips.append(clip)
    #     clip = CompositeVideoClip(clips)
    #     return clip

    # def burn(self, out_path: str) -> None:
    #     subtitle_clip = self.get_subtitle_clip()
    #     if self.render_offset:
    #         subtitle_clip = subtitle_clip.set_start(self.render_offset)
    #     clips = [self.base_clip, subtitle_clip]
    #     video = CompositeVideoClip(clips)
    #     video.write_videofile(out_path)

    def parse_word_segments(
        self,
        word_segments: List[WordSegment],
    ) -> List[Tuple[str, float]]:
        parsed = []
        for i, word_segment in enumerate(word_segments):
            text = word_segment["word"]
            start = word_segment["start"]
            if i < len(word_segments) - 1:
                end = word_segments[i + 1]["start"]
            else:
                end = word_segment["end"]
            duration = end - start
            parsed.append((text, duration))
        return parsed

    @measure
    def burn(self, out_path: str = "out.mp4") -> None:

        ffmpeg_command = [
            "ffmpeg",
            "-i",
            self.base_video,
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

        word_segments = self.transcript["word_segments"]

        try:
            for text, duration in self.parse_word_segments(word_segments):
                n = int(duration * self.fps)
                for i in range(n):
                    t = i / self.fps
                    img = self.get_text_image(text, scale=pop_up(t))
                    img_bytes = np.array(img).tobytes()
                    process.stdin.write(img_bytes)
        finally:
            process.stdin.close()
            process.wait()
