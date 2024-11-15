from burner import Burner, SubtitleOptions
from pathlib import Path
from time import time

input_path = Path("/Users/ryan/Desktop/burner/sample/1.mp4")

# start = time()
with Burner(input_path, None, "tiny.en") as burner:
    print(burner)
    # with Burner(
    #     "sample/input.mp4", transcript="sample/audio.json", whisper_model="tiny.en"
    # ) as burner:
    # options = SubtitleOptions(
    #     font_size=90,
    #     font_fill=(255, 255, 0),
    #     stroke_width=8,
    #     render_offset=-0.15,
    # )
    # burner.burn("output.mp4", options=options)
# end = time()
# print("Elapsed", end - start)
