import re

from django.core.exceptions import ValidationError

# Allowlisted, ordinary-link YouTube URL formats. We only ever store and
# redirect to these — the backend never fetches the URL content, and we
# never scrape, download, rehost, or bypass playback restrictions. See the
# brief's "YouTube handling" section.
_YOUTUBE_HOST_PATTERNS = (
    re.compile(
        r"^https://(www\.)?youtube\.com/watch\?v=[\w-]{6,}(&[\w.=&%-]*)?$"
    ),
    re.compile(r"^https://(www\.)?youtube\.com/embed/[\w-]{6,}(\?[\w.=&%-]*)?$"),
    re.compile(r"^https://youtu\.be/[\w-]{6,}(\?[\w.=&%-]*)?$"),
    # Clearly-marked local placeholder, for seed/example content only.
    re.compile(r"^https://www\.youtube\.com/watch\?v=PLACEHOLDER$"),
)


def validate_youtube_url(value: str) -> None:
    """
    Reject anything that isn't a recognized, ordinary YouTube link format
    (or our explicit seed-data placeholder). This is a format allowlist
    only — the backend never fetches the URL.
    """
    if not any(pattern.match(value) for pattern in _YOUTUBE_HOST_PATTERNS):
        raise ValidationError(
            "Enter a standard youtube.com/watch, youtube.com/embed, or "
            "youtu.be link.",
            code="invalid_youtube_url",
        )
