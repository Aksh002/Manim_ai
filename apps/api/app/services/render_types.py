from dataclasses import dataclass


class RenderTimeoutError(Exception):
    pass


@dataclass
class RenderResult:
    video_file: str
