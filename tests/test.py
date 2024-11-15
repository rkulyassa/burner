from burner import Burner, SubtitleOptions
from pathlib import Path
from time import time

input_path = Path("/Users/ryan/Desktop/burner/sample/1.mp4")

# start = time()
with Burner(input_path, transcript=None, whisper_model="tiny.en") as burner:
    # with Burner(
    #     "sample/input.mp4", transcript="sample/audio.json", whisper_model="tiny.en"
    # ) as burner:
    options = SubtitleOptions(
        font_size=90.0,
        stroke_width=8,
        render_offset=-0.15,
    )
    out_path = Path(__file__).parent / "output.mp4"
    burner.burn(out_path, options=options)
# end = time()
# print("Elapsed", end - start)
