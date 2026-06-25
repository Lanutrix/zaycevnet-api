"""Minimal usage example for the zaycevnet client.

Replace ``STATIC_KEY`` with a real application key before running.
"""

from zaycevnet import ZaycevClient

STATIC_KEY = "static_key"


def main() -> None:
    with ZaycevClient(STATIC_KEY) as client:
        client.authenticate()

        print("Suggestions for 'aa':", client.autocomplete("aa").terms[:5])

        result = client.search("ZZ TOP", page=1)
        print("Pages:", result.pages_count)
        if result.artist:
            print("Artist:", result.artist.name)
        for track in result.tracks[:5]:
            print(f"  {track.artist_name} - {track.track} ({track.duration})")


if __name__ == "__main__":
    main()
