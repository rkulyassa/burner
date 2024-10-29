from burner import Burner

burner = Burner(
    base_video="tests/sample/1.mp4",
    transcript="tests/sample/1.json",
    font_path="fonts/Montserrat-Black.ttf",
    font_size=90,
    fill=(255, 255, 0),
    stroke_width=8,
    stroke_fill=(0, 0, 0),
    render_offset=-0.15,
)
burner.burn()
# burner.save_text_frames()

# text_clip = burner.get_text_clip("Hello world", 0.5, 2)
# text_clip.write_videofile("out.mp4")

# img = burner.get_text_img("Hello world")
# img.save("out.png")
