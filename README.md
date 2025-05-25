# burner

### Motivation
In the modern content space, subtitling videos has become standard practice, especially for short-form content. Many existing tools for this are paywalled or limited in functionality. **burner** aims to be a FOSS alternative providing advanced subtitling capabilities and simple implementation in Python.

### Workflow
1. Transcribe audio with [whisperX](https://github.com/m-bain/whisperX)
2. Create text frames with [Pillow](https://python-pillow.org/)
3. Burn subtitles and render with [ffmpeg](https://www.ffmpeg.org/)

### Usage
```python
from burner import Burner, SubtitleOptions

with Burner("input.mp4") as burner:
    options = SubtitleOptions(font_size=90.0, font_fill=(255, 255, 0))
    burner.burn("output.mov", options=options)
```

### Sample Output
Note: accuracy processing time are dependent on your machine and the [whisper model](https://huggingface.co/collections/openai/whisper-release-6501bba2cf999715fd953013) you're running. **burner** is really only responsible for the subtitle generation.

https://github.com/user-attachments/assets/f4dbbc06-6c42-49ec-a776-b25b4f9108e8

