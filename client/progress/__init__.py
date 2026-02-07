"""Progress client module for Trakt API."""

from typing import Final

from .client import ProgressClient
from .playback import PlaybackClient
from .show_progress import ShowProgressClient

__all__: Final[list[str]] = [
    "PlaybackClient",
    "ProgressClient",
    "ShowProgressClient",
]
