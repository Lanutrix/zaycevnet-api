"""Typed data models for the Zaycev.net API.

Every model is a plain :class:`dataclasses.dataclass`. The raw API speaks
``camelCase`` JSON, so each model knows how to build itself from a decoded
response via :meth:`ApiObject.from_api`, which transparently maps
``camelCase`` keys onto ``snake_case`` fields and hydrates nested models.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Any, List, Optional, Union, get_args, get_origin, get_type_hints

__all__ = [
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
]


def _snake_to_camel(name: str) -> str:
    """Convert ``snake_case`` to the ``camelCase`` used by the API."""

    head, *tail = name.split("_")
    return head + "".join(word[:1].upper() + word[1:] for word in tail)


def _convert(type_hint: Any, value: Any) -> Any:
    """Coerce a raw JSON ``value`` into the annotated ``type_hint``."""

    origin = get_origin(type_hint)

    if origin is Union:  # typically Optional[...]
        inner = next(arg for arg in get_args(type_hint) if arg is not type(None))
        return _convert(inner, value) if value is not None else None

    if origin in (list, List):
        (item_hint,) = get_args(type_hint)
        return [_convert(item_hint, item) for item in (value or [])]

    if isinstance(type_hint, type) and issubclass(type_hint, ApiObject):
        return type_hint.from_api(value)

    return value


class ApiObject:
    """Mixin that builds a dataclass instance from a decoded API payload."""

    @classmethod
    def from_api(cls, data: Optional[dict]):
        if data is None:
            return None

        hints = get_type_hints(cls)
        kwargs = {}
        for f in fields(cls):  # type: ignore[arg-type]
            key = f.metadata.get("json") or _snake_to_camel(f.name)
            if key in data:
                kwargs[f.name] = _convert(hints[f.name], data[key])
        return cls(**kwargs)


@dataclass
class Token(ApiObject):
    """An auth handshake token (``hello`` / ``auth`` responses)."""

    token: str = ""


@dataclass
class Artist(ApiObject):
    id: int = 0
    name: str = ""
    about: str = ""
    image_uri: str = ""
    small_image_uri: str = ""


@dataclass
class Track(ApiObject):
    """A track as returned by ``top``, ``search`` and ``genre`` listings."""

    id: int = 0
    track: str = ""
    artist_id: int = 0
    artist_name: str = ""
    artist_image_url_square100: str = ""
    artist_image_url_square250: str = ""
    artist_image_url_top917: str = ""
    bitrate: int = 0
    duration: str = ""
    size: float = 0.0
    count: int = 0
    date: int = 0
    last_stamp: int = 0
    user_id: int = 0
    active: bool = False
    block: bool = False
    phantom: bool = False
    has_ring_back_tone: bool = False


@dataclass
class TrackList(ApiObject):
    """A paginated list of tracks."""

    page: int = 0
    pages_count: int = 0
    tracks: List[Track] = field(default_factory=list)


@dataclass
class Top(TrackList):
    """The chart of most popular tracks."""


@dataclass
class Genre(TrackList):
    """Tracks belonging to a single genre."""


@dataclass
class SearchResult(ApiObject):
    page: int = 0
    pages_count: int = 0
    artist: Optional[Artist] = None
    suggest_list: List[str] = field(default_factory=list)
    tracks: List[Track] = field(default_factory=list)


@dataclass
class MusicSet(ApiObject):
    """Metadata for a curated playlist ("music set")."""

    id: int = 0
    name: str = ""
    about: str = ""
    url: str = ""
    image_url: str = ""
    image_url_top917: str = ""
    small_image_url: str = ""
    create_date: int = 0
    publish_date: int = 0
    tracks_count: int = 0


@dataclass
class MusicSetList(ApiObject):
    items: List[MusicSet] = field(default_factory=list, metadata={"json": "list"})
    page: int = 0
    pages_count: int = 0

    @classmethod
    def from_api(cls, data: Optional[dict]):
        if data is None:
            return None
        # Pagination lives inside the nested "musicsetTypeId" object.
        pagination = data.get("musicsetTypeId") or {}
        merged = {**data, "page": pagination.get("page", 0),
                  "pagesCount": pagination.get("pagesCount", 0)}
        return super().from_api(merged)


@dataclass
class MusicSetTrack(ApiObject):
    track_id: int = 0
    track: str = ""
    full_name: str = ""
    ord: int = 0
    artist_id: int = 0
    artist_name: str = ""
    artist_image_url_square100: str = ""
    artist_image_url_square250: str = ""
    artist_image_url_square800: str = ""
    artist_image_url_top917: str = ""
    bitrate: int = 0
    duration: str = ""
    size: float = 0.0
    dl_url: str = ""
    play_url: str = ""


@dataclass
class MusicSetDetail(ApiObject):
    musicset: Optional[MusicSet] = None
    tracks: List[MusicSetTrack] = field(default_factory=list)


@dataclass
class RightPossessor(ApiObject):
    name: str = ""
    url: str = ""
    picture_url: str = ""


@dataclass
class Lyrics(ApiObject):
    original: List[str] = field(default_factory=list)


@dataclass
class TrackInfo(ApiObject):
    name: str = ""
    artist_id: int = 0
    artist_name: str = ""
    artist_image_url_square100: str = ""
    artist_image_url_square250: str = ""
    artist_image_url_top917: str = ""
    bitrate: int = 0
    created: int = 0
    duration: int = 0
    size: float = 0.0
    user_id: int = 0
    user_name: str = ""
    lyric_author: List[str] = field(default_factory=list)
    music_author: List[str] = field(default_factory=list)
    lyrics: Optional[Lyrics] = None
    right_possessors: List[RightPossessor] = field(default_factory=list)


@dataclass
class TrackDetail(ApiObject):
    rating: float = 0.0
    rbt_url: str = ""
    track: Optional[TrackInfo] = None


@dataclass
class AutoComplete(ApiObject):
    terms: List[str] = field(default_factory=list)


@dataclass
class Options(ApiObject):
    options: str = ""

    def as_list(self) -> List[str]:
        """Split the raw ``;``-separated options string into a list."""

        return [item for item in self.options.split(";") if item]


@dataclass
class MediaLink(ApiObject):
    """A playable / downloadable media URL pair."""

    url: str = ""
    rbt_url: str = ""


@dataclass
class Download(MediaLink):
    """Direct download link for a track."""


@dataclass
class Play(MediaLink):
    """Streaming link for a track."""
