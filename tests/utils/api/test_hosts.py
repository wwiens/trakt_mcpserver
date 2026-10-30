"""Tests for Trakt host classification."""

import pytest

from utils.api.hosts import is_auth_host_url


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://auth.trakt.tv/oauth/token", True),
        ("https://api.trakt.tv/sync/history", False),
        ("/sync/history", False),
        ("https://auth.trakt.tv.evil.example/oauth/token", False),
    ],
)
def test_is_auth_host_url(url: str, expected: bool) -> None:
    assert is_auth_host_url(url) is expected
