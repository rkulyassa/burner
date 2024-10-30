from ..burner import Burner, SubtitleOptions
from time import time

start = time()
with Burner("sample/1.mp4", transcript="sample/1.json") as burner:
    # with Burner(
    #     "sample/input.mp4", transcript="sample/audio.json", whisper_model="tiny.en"
    # ) as burner:
    options = SubtitleOptions(
        font_size=75, font_fill=(255, 255, 0), render_offset=-0.15
    )
    burner.burn("output2.mp4", options=options)
end = time()
print("Elapsed", end - start)
