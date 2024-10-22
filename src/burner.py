from PIL import Image, ImageFont, ImageDraw, ImageColor
from typing import Tuple


class Burner:
    def __init__(
        self,
        video_path: str,
        video_size: Tuple[float, float],
        transcript: str,
        font_path: str,
        font_size: float,
        fill: Tuple[int, int, int],
        stroke_width: float,
        stroke_fill: Tuple[int, int, int],
        capitalize: bool = True,
    ):
        self.video_path = video_path
        self.video_size = video_size
        self.transcript = transcript
        self.font = ImageFont.truetype(font_path, font_size)
        self.fill = fill
        self.stroke_width = stroke_width
        self.stroke_fill = stroke_fill
        self.capitalize = capitalize

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


burner = Burner(
    video_path="../sample/1.mp4",
    transcript="../sample/1.json",
    font_path="../fonts/Montserrat-Black.ttf",
    font_size=90,
    video_size=(1080, 1920),
    fill=(255, 255, 0),
    stroke_width=8,
    stroke_fill=(0, 0, 0),
)

img = burner.get_text_img("Hello world")
img.save("out.png")
