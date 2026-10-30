"""Classify request URLs by Trakt host."""

from urllib.parse import urlsplit

from config.auth import TRAKT_AUTH_HOST


def is_auth_host_url(url: str) -> bool:
    """Check whether a URL targets the OAuth host rather than the API host."""
    return urlsplit(url).hostname == TRAKT_AUTH_HOST
