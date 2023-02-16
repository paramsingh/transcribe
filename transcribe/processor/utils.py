from urllib import parse
from urllib.parse import ParseResult

import yt_dlp


def is_playlist_link(link: str):
    parsed_url = parse.urlparse(link, scheme='https')
    return _is_playlist_path(parsed_url) or _is_playlist_in_watch_query(parsed_url)


def _is_playlist_path(link: ParseResult):
    # https://www.youtube.com/playlist?list=PL8HowI-L-3_9bkocmR3JahQ4Y-Pbqs2Nt
    return link.path == "/playlist"


def _is_playlist_in_watch_query(link: ParseResult):
    # https://www.youtube.com/watch?v=vwn77cUarTs&list=PL8HowI-L-3_9bkocmR3JahQ4Y-Pbqs2Nt&index=1
    query = {element[0]: element[1] for element in [q.split("=") for q in link.query.split("&")]}
    return link.path == "/watch" and 'list' in query.keys()


def get_playlist_items(playlist_link: str):
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "extract_flat": "in_playlist",
        "forcejson": True
    }
    result = yt_dlp.YoutubeDL(ydl_opts).extract_info(
        playlist_link,
        download=False
    )
    return [entry["url"] for entry in result["entries"]]

