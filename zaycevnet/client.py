"""Synchronous client for the Zaycev.net external API."""

from __future__ import annotations

import hashlib
from typing import Any, Optional, Type, TypeVar

import requests

from .exceptions import ApiError, AuthenticationError
from .models import (
    ApiObject,
    Artist,
    AutoComplete,
    Download,
    Genre,
    MusicSetDetail,
    MusicSetList,
    Options,
    Play,
    SearchResult,
    Token,
    Top,
    TrackDetail,
)

__all__ = ["ZaycevClient", "md5_hash"]

DEFAULT_BASE_URL = "https://api.zaycev.net/external"
DEFAULT_TIMEOUT = 30.0

M = TypeVar("M", bound=ApiObject)


def md5_hash(text: str) -> str:
    """Return the hex-encoded MD5 digest of ``text`` (used for auth)."""

    return hashlib.md5(text.encode("utf-8")).hexdigest()


class ZaycevClient:
    """A thin, typed wrapper around the Zaycev.net external API.

    The two-step authentication handshake mirrors the official mobile client:
    a ``hello`` request yields a short-lived token, which is hashed together
    with the static key to obtain a persistent ``access_token``.

    Args:
        static_key: The application's static key (required to authenticate).
        access_token: A previously obtained access token, to skip the
            handshake.
        session: An optional pre-configured :class:`requests.Session`.
        timeout: Per-request timeout in seconds.
        base_url: Override for the API root, mainly useful in tests.

    Example:
        >>> client = ZaycevClient("static_key")
        >>> client.authenticate()
        >>> result = client.search("ZZ TOP")
        >>> result.tracks[0].artist_name
    """

    def __init__(
        self,
        static_key: str,
        *,
        access_token: Optional[str] = None,
        session: Optional[requests.Session] = None,
        timeout: float = DEFAULT_TIMEOUT,
        base_url: str = DEFAULT_BASE_URL,
    ) -> None:
        self.static_key = static_key
        self.access_token = access_token
        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self._session = session or requests.Session()
        self._owns_session = session is None
        self._hello_token: Optional[str] = None

    # -- context manager ---------------------------------------------------

    def __enter__(self) -> "ZaycevClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying session if it was created by the client."""

        if self._owns_session:
            self._session.close()

    # -- authentication ----------------------------------------------------

    def authenticate(self) -> str:
        """Perform the hello/auth handshake and store the access token.

        Returns:
            The freshly obtained access token.
        """

        if not self.static_key:
            raise AuthenticationError("A non-empty static key is required.")

        hello = self._request("/hello", model=Token, authenticated=False)
        self._hello_token = hello.token

        signature = md5_hash(self._hello_token + self.static_key)
        auth = self._request(
            "/auth",
            params={"code": self._hello_token, "hash": signature},
            model=Token,
            authenticated=False,
        )
        self.access_token = auth.token
        return self.access_token

    # -- endpoints ---------------------------------------------------------

    def search(
        self,
        query: str,
        *,
        page: int = 1,
        search_type: str = "all",
        sort: str = "",
        style: str = "",
    ) -> SearchResult:
        """Search the catalog for ``query``."""

        params = {
            "query": query,
            "page": page,
            "type": search_type,
            "sort": sort,
            "style": style,
        }
        return self._request("/search", params=params, model=SearchResult)

    def autocomplete(self, query: str) -> AutoComplete:
        """Return search-term suggestions for ``query``."""

        return self._request(
            "/autocomplete", params={"query": query}, model=AutoComplete
        )

    def top(self, page: int = 1) -> Top:
        """Return a page of the popularity chart."""

        return self._request("/top", params={"page": page}, model=Top)

    def musicset_list(self, page: int = 0) -> MusicSetList:
        """Return a page of curated music sets (playlists)."""

        return self._request(
            "/musicset/list", params={"page": page}, model=MusicSetList
        )

    def musicset_detail(self, musicset_id: int) -> MusicSetDetail:
        """Return a single music set together with its tracks."""

        return self._request(
            "/musicset/detail", params={"id": musicset_id}, model=MusicSetDetail
        )

    def genre(self, genre: str, page: int = 1) -> Genre:
        """Return a page of tracks for a given ``genre``."""

        return self._request(
            "/genre", params={"genre": genre, "page": page}, model=Genre
        )

    def artist(self, artist_id: int) -> Artist:
        """Return information about a single artist."""

        data = self._request(f"/artist/{artist_id}")
        return Artist.from_api(data.get("artist", {}))

    def track(self, track_id: int) -> TrackDetail:
        """Return detailed information about a single track."""

        return self._request(f"/track/{track_id}", model=TrackDetail)

    def options(self) -> Options:
        """Return the raw service options string."""

        return self._request("/options", model=Options)

    def download(self, track_id: int) -> Download:
        """Return a direct download link for a track."""

        return self._request(
            f"/track/{track_id}/download/",
            params={"encoded_identifier": ""},
            model=Download,
        )

    def play(self, track_id: int) -> Play:
        """Return a streaming link for a track."""

        return self._request(
            f"/track/{track_id}/play",
            params={"encoded_identifier": ""},
            model=Play,
        )

    # -- transport ---------------------------------------------------------

    def _request(
        self,
        path: str,
        *,
        params: Optional[dict] = None,
        model: Optional[Type[M]] = None,
        authenticated: bool = True,
    ):
        """Issue a GET request and optionally parse it into ``model``."""

        params = dict(params or {})
        if authenticated:
            if not self.access_token:
                raise AuthenticationError(
                    "Not authenticated. Call authenticate() or pass an "
                    "access_token first."
                )
            params["access_token"] = self.access_token

        try:
            response = self._session.get(
                self.base_url + path, params=params, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise ApiError(f"Request to {path} failed: {exc}") from exc

        if response.status_code != 200:
            raise ApiError(
                f"Unexpected status code {response.status_code} for {path}.",
                status_code=response.status_code,
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise ApiError(f"Invalid JSON in response for {path}.") from exc

        self._raise_for_service_error(data)

        if model is None:
            return data
        return model.from_api(data)

    @staticmethod
    def _raise_for_service_error(data: Any) -> None:
        """Raise :class:`ApiError` if the payload carries an API error."""

        if isinstance(data, dict) and isinstance(data.get("error"), dict):
            error = data["error"]
            raise ApiError(
                error.get("text", "Unknown API error."),
                code=error.get("code"),
            )
