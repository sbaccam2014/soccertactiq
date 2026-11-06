"""
A narrow, deliberate exception to "the backend never fetches the URL
content" (see validators.py): this module calls YouTube's own Data API
v3 to read a video's public description field, so coaches/admins don't
have to retype it by hand. No scraping, no downloading video/audio, no
bypassing playback restrictions — just one metadata field from
YouTube's documented API, using an API key (see settings.YOUTUBE_API_KEY).
"""

import json
import logging
import re
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

_VIDEOS_ENDPOINT = "https://www.googleapis.com/youtube/v3/videos"

_VIDEO_ID_PATTERNS = (
    re.compile(r"[?&]v=([\w-]{6,})"),
    re.compile(r"youtube\.com/shorts/([\w-]{6,})"),
    re.compile(r"youtube\.com/embed/([\w-]{6,})"),
    re.compile(r"youtu\.be/([\w-]{6,})"),
)


def extract_video_id(video_url: str) -> str | None:
    """Pulls the 11-character YouTube video ID out of any of our
    allowlisted URL formats (see validators.validate_youtube_url)."""
    for pattern in _VIDEO_ID_PATTERNS:
        match = pattern.search(video_url)
        if match:
            return match.group(1)
    return None


def fetch_description(video_url: str) -> str:
    """
    Looks up a video's description via the YouTube Data API v3. Returns
    an empty string (never raises) if YOUTUBE_API_KEY isn't configured,
    the URL's video ID can't be parsed, the video doesn't exist, or the
    request fails for any reason — description auto-fill is a
    best-effort convenience, not something that should block saving a
    video.
    """
    if not settings.YOUTUBE_API_KEY:
        logger.debug(
            "YOUTUBE_API_KEY is not set; skipping description auto-fill "
            "for %s.",
            video_url,
        )
        return ""

    video_id = extract_video_id(video_url)
    if not video_id or video_id == "PLACEHOLDER":
        return ""

    query = urllib.parse.urlencode(
        {"part": "snippet", "id": video_id, "key": settings.YOUTUBE_API_KEY}
    )
    request = urllib.request.Request(f"{_VIDEOS_ENDPOINT}?{query}")

    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        logger.warning(
            "Couldn't fetch YouTube description for %s: %s", video_url, exc
        )
        return ""

    items = data.get("items") or []
    if not items:
        return ""
    return items[0].get("snippet", {}).get("description", "") or ""
