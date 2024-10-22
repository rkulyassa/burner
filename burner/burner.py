from PIL import Image, ImageFont, ImageDraw, ImageColor
from moviepy.editor import ImageSequenceClip, VideoFileClip, CompositeVideoClip
from typing import Tuple, Dict
from .animations import pop_up
from .types import Transcript
import numpy as np
import json


class Burner:
    def __init__(
        self,
        video_path: str,
        video_size: Tuple[float, float],
        transcript_path: str,
        font_path: str,
        font_size: float,
        fill: Tuple[int, int, int],
        stroke_width: float,
        stroke_fill: Tuple[int, int, int],
        capitalize: bool = True,
    ):
        self.video_path = video_path
        self.video_size = video_size
        self.transcript = self._load_transcript(transcript_path)
        self.font = ImageFont.truetype(font_path, font_size)
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill
        self.capitalize = capitalize

    def _load_transcript(self, transcript_path: str) -> Transcript:
        with open(transcript_path) as f:
            transcript_data = json.load(f)
        return transcript_data

    def _get_center(self) -> Tuple[float, float]:
        w, h = self.video_size
        return (w / 2, h / 2)

    def get_text_img(self, text: str) -> Image.Image:
        if self.capitalize:
            text = text.upper()
        img = Image.new(mode="RGBA", size=self.video_size)
        draw = ImageDraw.Draw(img)
        draw.text(
            xy=self._get_center(),
            text=text,
            fill=self.fill,
            font=self.font,
            anchor="mm",
            language="en",
            stroke_width=self.stroke_width,
            stroke_fill=self.stroke_fill,
        )
        # draw.circle(self._get_center(), 20, fill=255)
        return img

    def get_text_clip(
        self, text: str, start: float, end: float, fps: int = 60
    ) -> ImageSequenceClip:
        duration = end - start
        img = self.get_text_img(text)
        w_i, h_i = img.size
        frames = []
        n = int(duration * fps)
        for i in range(n):
            t = i / fps
            scale = pop_up(t)
            w = int(w_i * scale)
            h = int(h_i * scale)
            container_img = img.copy()
            text_img = img.resize((w, h))
            offset = ((w_i - w) // 2, (h_i - h) // 2)
            container_img.paste(text_img, offset)
            frames.append(np.array(container_img))
        clip = ImageSequenceClip(frames, fps=fps)
        clip: ImageSequenceClip = clip.set_start(start)
        clip = clip.set_duration(duration)
        return clip

    def get_subtitle_clip(self):
        clips = []
        word_segments = self.transcript["word_segments"]
        for i, word_segment in enumerate(word_segments):
            text = word_segment["word"]
            start = word_segment["start"]
            if i < len(word_segments) - 1:
                end = word_segments[i + 1]["start"]
            else:
                end = word_segment["end"]
            clip = self.get_text_clip(text, start, end)
            clips.append(clip)
        clip = CompositeVideoClip(clips)
        return clip

    def burn(self, out_path: str) -> None:
        base_clip = VideoFileClip(self.video_path)
        subtitle_clip = self.get_subtitle_clip()
        clips = [base_clip, subtitle_clip]
        video = CompositeVideoClip(clips)
        video.write_videofile(out_path)


# burner = Burner(
#     video_path="sample/1.mp4",
#     transcript_path="sample/1.json",
#     font_path="fonts/Montserrat-Black.ttf",
#     font_size=90,
#     video_size=(1080, 1920),
#     fill=(255, 255, 0),
#     stroke_width=8,
#     stroke_fill=(0, 0, 0),
# )
# burner.burn("out.mp4")

# text_clip = burner.get_text_clip("Hello world", 0.5, 2)
# text_clip.write_videofile("out.mp4")

# img = burner.get_text_img("Hello world")
# img.save("out.png")
