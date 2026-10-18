"""Tests for BaseClient request context and header preparation."""

import os
from collections.abc import Generator
from unittest.mock import patch

import pytest

from client.base import BaseClient
from utils.api.request_context import (
    clear_current_context,
    get_current_context,
)


@pytest.fixture(autouse=True)
def isolated_context() -> Generator[None, None, None]:
    clear_current_context()
    yield
    clear_current_context()


@pytest.fixture
def client() -> BaseClient:
    with patch.dict(os.environ, {"TRAKT_CLIENT_ID": "test_id"}):
        return BaseClient()


def test_api_request_after_oauth_call_gets_its_own_resource_context(
    client: BaseClient,
) -> None:
    """A token refresh earlier in the task must not label the API call's errors."""
    client._prepare_request("https://auth.trakt.tv/oauth/token", "POST")  # pyright: ignore[reportPrivateUsage]
    oauth_context = get_current_context()
    assert oauth_context is not None
    assert oauth_context.resource_type is None

    client._prepare_request("/shows/bad-slug", "GET")  # pyright: ignore[reportPrivateUsage]

    api_context = get_current_context()
    assert api_context is not None
    assert api_context.endpoint == "/shows/bad-slug"
    assert (api_context.resource_type, api_context.resource_id) == (
        "shows",
        "bad-slug",
    )
    assert api_context.correlation_id == oauth_context.correlation_id


def test_first_api_context_is_kept_for_later_requests(client: BaseClient) -> None:
    client._prepare_request("/shows/breaking-bad", "GET")  # pyright: ignore[reportPrivateUsage]
    client._prepare_request("/shows/breaking-bad/seasons", "GET")  # pyright: ignore[reportPrivateUsage]

    context = get_current_context()
    assert context is not None
    assert context.endpoint == "/shows/breaking-bad"


def test_oauth_call_mid_task_gets_its_own_context(client: BaseClient) -> None:
    """A refresh during an API call is labelled with the OAuth endpoint."""
    client._prepare_request("/shows/breaking-bad", "GET")  # pyright: ignore[reportPrivateUsage]
    api_context = get_current_context()
    client._prepare_request("https://auth.trakt.tv/oauth/token", "POST")  # pyright: ignore[reportPrivateUsage]

    oauth_context = get_current_context()
    assert oauth_context is not None and api_context is not None
    assert oauth_context.endpoint == "https://auth.trakt.tv/oauth/token"
    assert oauth_context.resource_type is None
    assert oauth_context.correlation_id == api_context.correlation_id
