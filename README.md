# burner

### Motivation
In the modern content space, subtitling videos has become standard practice, especially for short-form content. Many existing tools for this are paywalled or limited in functionality. **burner** aims to be a FOSS alternative providing advanced subtitling capabilities and simple implementation in Python.

### Concept
**burner** uses two main libraries, [Pillow](https://python-pillow.org/) and [moviepy](https://zulko.github.io/moviepy/). The process is simple: given a transcript file, Pillow creates images of each text frame, and moviepy concatenates all the frames into a video clip, which gets burned onto an existing video. There is potential for alot of functionality here, i.e. text animations.

### Usage
For now, download and import locally. I'll upload this to PyPI when I get around to it.
```python
from burner import Burner, SubtitleOptions

with Burner("input.mp4") as burner:
    options = SubtitleOptions(font_size=90.0, font_fill=(255, 255, 0))
    burner.burn("output.mp4", options=options)
```
