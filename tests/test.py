from ..burner import Burner, SubtitleOptions
from time import time

start = time()
with Burner("sample/1.mp4", transcript="sample/1.json") as burner:
    # with Burner(
    #     "sample/input.mp4", transcript="sample/audio.json", whisper_model="tiny.en"
    # ) as burner:
    options = SubtitleOptions(
        position="top",
        font_size=90,
        font_fill=(255, 255, 0),
        stroke_width=8,
        render_offset=-0.15,
    )
    burner.burn("output.mp4", options=options)
end = time()
print("Elapsed", end - start)
