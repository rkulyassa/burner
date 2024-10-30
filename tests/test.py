from burner import Burner, SubtitleOptions

with Burner("sample/1.mp4") as burner:
    options = SubtitleOptions(font_fill=(255, 255, 0))
    burner.burn("out.mp4", options=options)
