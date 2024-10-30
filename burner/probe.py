import subprocess
from typing import Tuple, Any

from ._typing import PathLike


class Probe:
    """
    Wrapper for ffprobe commands
    """

    def __init__(self, video_path: PathLike) -> None:
        self._video_path = video_path

        output = self._extract("stream=r_frame_rate")
        num, denom = map(int, output.split("/"))
        self._fps = num / denom

        self._frame_count = int(self._extract("stream=nb_frames"))
        self._duration = float(self._extract("format=duration"))

        output = self._extract("stream=width,height")
        w, h = map(int, output.split(","))
        self._size = (w, h)
        self._center = (w / 2, h / 2)

    @property
    def video_path(self) -> str:
        return self._video_path

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def frame_count(self) -> int:
        return self._frame_count

    @property
    def duration(self) -> float:
        return self._duration

    @property
    def size(self) -> Tuple[int, int]:
        return self._size

    @property
    def center(self) -> Tuple[int, int]:
        return self._center

    def _extract(self, target: str) -> str:
        command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            target,
            "-of",
            "csv=p=0",
            str(self._video_path),
        ]
        output = subprocess.check_output(command, text=True).strip()
        return output
