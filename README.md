# zaycevnet-api

A clean, typed Python client for the [Zaycev.net](https://zaycev.net) external API.

This is a from-scratch Python port of the Go library
[`pixfid/go-zaycevnet`](https://github.com/pixfid/go-zaycevnet): same endpoints,
idiomatic Python design — dataclass models, explicit exceptions, and a small
HTTP layer built on `requests`.

## Install

```bash
pip install -r requirements.txt
# or, as a package:
pip install .
```

Requires Python 3.8+ and `requests`.

## Usage

```python
from zaycevnet import ZaycevClient

with ZaycevClient("static_key") as client:
    client.authenticate()

    result = client.search("ZZ TOP", page=1)
    print(result.pages_count)
    if result.artist:
        print(result.artist.name)

    for track in result.tracks:
        print(track.artist_name, "-", track.track)
```

Already have an access token? Skip the handshake:

```python
client = ZaycevClient("static_key", access_token="stored_token")
```

## Authentication

`authenticate()` reproduces the official two-step handshake:

1. `GET /hello` returns a short-lived token.
2. `MD5(hello_token + static_key)` is sent to `GET /auth`, which returns the
   persistent `access_token` used for every subsequent call.

## Supported methods

| Method | Returns |
| --- | --- |
| `authenticate()` | `str` (access token) |
| `search(query, page=1, search_type="all", sort="", style="")` | `SearchResult` |
| `autocomplete(query)` | `AutoComplete` |
| `top(page=1)` | `Top` |
| `musicset_list(page=0)` | `MusicSetList` |
| `musicset_detail(musicset_id)` | `MusicSetDetail` |
| `genre(genre, page=1)` | `Genre` |
| `artist(artist_id)` | `Artist` |
| `track(track_id)` | `TrackDetail` |
| `options()` | `Options` |
| `download(track_id)` | `Download` |
| `play(track_id)` | `Play` |

All models are dataclasses (see `zaycevnet/models.py`) with `snake_case`
attributes hydrated automatically from the API's `camelCase` JSON.

## Errors

* `AuthenticationError` — missing static key or access token.
* `ApiError` — non-200 status, invalid JSON, or an error object in the body
  (carries `status_code` / `code` when available).
* `ZaycevError` — base class for both.

## License

BSD 3-Clause. See [LICENSE](LICENSE).
