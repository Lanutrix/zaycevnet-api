"""A clean, typed Python client for the Zaycev.net external API.

Quick start::

    from zaycevnet import ZaycevClient

    with ZaycevClient("static_key") as client:
        client.authenticate()
        for track in client.top().tracks:
            print(track.artist_name, "-", track.track)
"""

from __future__ import annotations

from .client import ZaycevClient, md5_hash
from .exceptions import ApiError, AuthenticationError, ZaycevError
from .models import (
    ApiObject,
    Artist,
    AutoComplete,
    Download,
    Genre,
    Lyrics,
    MediaLink,
    MusicSet,
    MusicSetDetail,
    MusicSetList,
    MusicSetTrack,
    Options,
    Play,
    RightPossessor,
    SearchResult,
    Token,
    Top,
    Track,
    TrackDetail,
    TrackInfo,
    TrackList,
)

__version__ = "0.1.0"

__all__ = [
    "ZaycevClient",
    "md5_hash",
    "ZaycevError",
    "AuthenticationError",
    "ApiError",
    "ApiObject",
    "Token",
    "Artist",
    "Track",
    "TrackList",
    "Top",
    "Genre",
    "SearchResult",
    "MusicSet",
    "MusicSetList",
    "MusicSetTrack",
    "MusicSetDetail",
    "RightPossessor",
    "Lyrics",
    "TrackInfo",
    "TrackDetail",
    "AutoComplete",
    "Options",
    "MediaLink",
    "Download",
    "Play",
    "__version__",
]
