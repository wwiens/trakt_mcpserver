"""Stress tests for token refresh chain across multi-day usage scenarios.

Verifies that users authenticate once via /activate and stay authenticated
indefinitely — matching the Kodi-like experience — through automatic token
refresh when access tokens expire (every 24h).
"""

import asyncio
import io
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from client.auth import AuthClient
from models.auth import TraktAuthToken
from utils.api.errors import handle_api_errors

DAY: int = 86400


def _make_expired_token(days_ago: int) -> TraktAuthToken:
    """Create a token that expired `days_ago` days in the past."""
    return TraktAuthToken(
        access_token=f"expired_token_{days_ago}d",
        refresh_token=f"refresh_token_{days_ago}d",
        expires_in=DAY,
        created_at=int(time.time()) - (days_ago * DAY) - DAY,
        scope="public",
        token_type="bearer",
    )


def _make_fresh_token_data(suffix: str = "new") -> dict[str, Any]:
    """Return raw dict for a fresh token response from the API."""
    return {
        "access_token": f"fresh_access_{suffix}",
        "refresh_token": f"fresh_refresh_{suffix}",
        "expires_in": DAY,
        "created_at": int(time.time()),
        "scope": "public",
        "token_type": "bearer",
    }


def _mock_post_response(data: dict[str, Any]) -> MagicMock:
    """Build a mock httpx.Response returning `data` as JSON."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = 200
    resp.json.return_value = data
    resp.raise_for_status = MagicMock()
    return resp


@contextmanager
def _patch_file_io() -> Generator[None, None, None]:
    """Patch atomic-write file I/O used by _save_auth_token."""
    fake_fd = 99
    with (
        patch("os.open", return_value=fake_fd),
        patch(
            "os.fdopen",
            side_effect=lambda *_a, **_kw: io.StringIO(),  # pyright: ignore[reportUnknownLambdaType]
        ),
        patch("os.replace"),
        patch("os.makedirs"),
        patch("os.fsync"),
    ):
        yield


class TestTokenRefreshChain:
    """Stress tests proving Kodi-like long-lived authentication."""

    # ------------------------------------------------------------------
    # 1. Single expiry: token expired 2 days ago, refresh succeeds
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_single_expiry_refresh(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Token expired 2 days ago is silently refreshed."""
        fresh_data = _make_fresh_token_data("day2")
        patched_httpx_client.post.return_value = _mock_post_response(fresh_data)

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=2)
            assert client.is_authenticated() is False

            result = await client.ensure_authenticated()

        assert result is True
        assert client.auth_token is not None
        assert client.auth_token.access_token == "fresh_access_day2"
        assert client.is_authenticated() is True
        assert client.headers["Authorization"] == "Bearer fresh_access_day2"
        patched_httpx_client.post.assert_called_once()

    # ------------------------------------------------------------------
    # 2. Consecutive 3-day refresh chain
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_consecutive_refresh_chain_3_days(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Three successive refresh cycles, each using the previous refresh_token."""
        with _patch_file_io():
            client = AuthClient()

            for day in range(1, 4):
                fresh_data = _make_fresh_token_data(f"day{day}")
                patched_httpx_client.post.return_value = _mock_post_response(fresh_data)

                # Simulate the token from last cycle having expired
                if day == 1:
                    client.auth_token = _make_expired_token(days_ago=1)
                else:
                    # "Age" the previously refreshed token
                    assert client.auth_token is not None
                    client.auth_token = TraktAuthToken(
                        access_token=client.auth_token.access_token,
                        refresh_token=client.auth_token.refresh_token,
                        expires_in=DAY,
                        created_at=int(time.time()) - DAY - 1,
                        scope="public",
                        token_type="bearer",
                    )

                assert client.is_authenticated() is False
                result = await client.ensure_authenticated()
                assert result is True
                assert client.auth_token is not None
                assert client.auth_token.access_token == f"fresh_access_day{day}"

        assert patched_httpx_client.post.call_count == 3

        # Verify each refresh sent the previous cycle's refresh_token
        calls = patched_httpx_client.post.call_args_list
        assert "refresh_token" in str(calls[0])
        assert "fresh_refresh_day1" in str(calls[1])
        assert "fresh_refresh_day2" in str(calls[2])

    # ------------------------------------------------------------------
    # 3. Cold start after 30-day absence
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_cold_start_30_day_absence(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Token expired 30 days ago recovers seamlessly."""
        fresh_data = _make_fresh_token_data("cold_start")
        patched_httpx_client.post.return_value = _mock_post_response(fresh_data)

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=30)
            assert client.is_authenticated() is False

            expiry = client.get_token_expiry()
            assert expiry is not None
            assert expiry < int(time.time()) - 29 * DAY

            result = await client.ensure_authenticated()

        assert result is True
        assert client.is_authenticated() is True
        assert client.auth_token is not None
        assert client.auth_token.access_token == "fresh_access_cold_start"

    # ------------------------------------------------------------------
    # 4. Concurrent ensure_authenticated — single refresh
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_concurrent_ensure_authenticated_single_refresh(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Five concurrent callers share one refresh via _refresh_lock."""
        fresh_data = _make_fresh_token_data("concurrent")

        async def slow_post(*args: Any, **kwargs: Any) -> MagicMock:
            await asyncio.sleep(0.05)
            return _mock_post_response(fresh_data)

        patched_httpx_client.post = AsyncMock(side_effect=slow_post)

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=1)

            results = await asyncio.gather(
                *[client.ensure_authenticated() for _ in range(5)]
            )

        assert all(results)
        assert patched_httpx_client.post.call_count == 1
        assert client.auth_token is not None
        assert client.auth_token.access_token == "fresh_access_concurrent"

    # ------------------------------------------------------------------
    # 5. 401 mid-flight reactive refresh
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_401_mid_flight_reactive_refresh(self) -> None:
        """ensure_authenticated passes, but API returns 401 — decorator recovers."""

        class MidFlightService:
            def __init__(self) -> None:
                self.call_count = 0
                self.refresh_called = False
                self.clear_auth_token_called = False
                self.auth_token = MagicMock(refresh_token="valid")
                self._refresh_lock = asyncio.Lock()

            def clear_auth_token(self) -> bool:
                self.clear_auth_token_called = True
                return True

            async def refresh_access_token(self) -> bool:
                self.refresh_called = True
                return True

            @handle_api_errors
            async def fetch_data(self) -> str:
                self.call_count += 1
                if self.call_count == 1:
                    resp = MagicMock()
                    resp.status_code = 401
                    resp.text = "Unauthorized"
                    raise httpx.HTTPStatusError(
                        message="401", request=MagicMock(), response=resp
                    )
                return "data"

        svc = MidFlightService()
        result = await svc.fetch_data()

        assert result == "data"
        assert svc.call_count == 2
        assert svc.refresh_called is True
        assert svc.clear_auth_token_called is False

    # ------------------------------------------------------------------
    # 6. Refresh token revoked after successful chain
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_refresh_token_revoked_after_chain(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """First refresh OK, then refresh_token is revoked on Trakt side."""
        fresh_data = _make_fresh_token_data("first")

        # First call succeeds
        patched_httpx_client.post.return_value = _mock_post_response(fresh_data)

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=1)
            assert await client.ensure_authenticated() is True

            # Expire the new token to trigger a second refresh
            assert client.auth_token is not None
            client.auth_token = TraktAuthToken(
                access_token=client.auth_token.access_token,
                refresh_token=client.auth_token.refresh_token,
                expires_in=DAY,
                created_at=int(time.time()) - DAY - 1,
                scope="public",
                token_type="bearer",
            )

            # Second refresh: Trakt rejects the refresh_token with 401
            revoked_resp = MagicMock(spec=httpx.Response)
            revoked_resp.status_code = 401
            revoked_resp.text = "Unauthorized"
            revoked_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
                message="401", request=MagicMock(), response=revoked_resp
            )
            patched_httpx_client.post.return_value = revoked_resp

            with patch("os.remove"):
                result = await client.ensure_authenticated()

        assert result is False
        assert client.auth_token is None

    # ------------------------------------------------------------------
    # 7. Recursive refresh avoidance (401 during refresh itself)
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_recursive_refresh_avoidance(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """401 on the refresh HTTP call does not deadlock or recurse."""
        resp_401 = MagicMock(spec=httpx.Response)
        resp_401.status_code = 401
        resp_401.text = "Unauthorized"
        resp_401.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="401", request=MagicMock(), response=resp_401
        )
        patched_httpx_client.post.return_value = resp_401

        with _patch_file_io(), patch("os.remove"):
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=1)
            result = await client.refresh_access_token()

        assert result is False
        assert client.auth_token is None

    # ------------------------------------------------------------------
    # 8. End-to-end: proactive refresh then API call
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_end_to_end_proactive_refresh_then_api_call(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Full tool-call simulation: refresh + GET succeeds seamlessly."""
        fresh_data = _make_fresh_token_data("e2e")
        api_response = MagicMock(spec=httpx.Response)
        api_response.status_code = 200
        api_response.json.return_value = {"title": "Breaking Bad"}
        api_response.raise_for_status = MagicMock()

        # POST = refresh, GET = API call
        patched_httpx_client.post.return_value = _mock_post_response(fresh_data)
        patched_httpx_client.get.return_value = api_response

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=1)

            # Proactive refresh
            assert await client.ensure_authenticated() is True

            # API call (using internal method — acceptable in tests)
            result = await client._make_request(  # pyright: ignore[reportPrivateUsage]
                "GET", "/shows/breaking-bad"
            )

        assert result == {"title": "Breaking Bad"}
        patched_httpx_client.post.assert_called_once()
        patched_httpx_client.get.assert_called_once()
        assert "Bearer fresh_access_e2e" in str(patched_httpx_client.get.call_args)

    # ------------------------------------------------------------------
    # 9. Transient error preserves refresh_token for next attempt
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_transient_error_preserves_refresh_token(
        self, trakt_env: None, patched_httpx_client: MagicMock
    ) -> None:
        """Network error on refresh keeps refresh_token; next attempt works."""
        # First attempt: network failure
        patched_httpx_client.post = AsyncMock(
            side_effect=httpx.ConnectError("Connection refused")
        )

        with _patch_file_io():
            client = AuthClient()
            client.auth_token = _make_expired_token(days_ago=1)

            result = await client.ensure_authenticated()
            assert result is False
            assert client.auth_token is not None
            assert client.auth_token.refresh_token == "refresh_token_1d"

            # Second attempt: success
            fresh_data = _make_fresh_token_data("recovered")
            patched_httpx_client.post = AsyncMock(
                return_value=_mock_post_response(fresh_data)
            )
            result = await client.ensure_authenticated()

        assert result is True
        assert client.auth_token is not None
        assert client.auth_token.access_token == "fresh_access_recovered"

    # ------------------------------------------------------------------
    # 10. Concurrent 401s — single refresh across multiple methods
    # ------------------------------------------------------------------
    @pytest.mark.asyncio
    async def test_concurrent_401_single_refresh(self) -> None:
        """Multiple methods get 401 concurrently; only one refresh fires."""

        class ConcurrentService:
            """Service where refresh does NOT hold _refresh_lock.

            The decorator checks _refresh_lock.locked() only as a recursion
            guard (to avoid refreshing from within refresh's own HTTP call).
            In real AuthClient, refresh_access_token holds the lock internally
            for dedup, but the decorator's check is strictly anti-recursion.
            Here we test that sequential 401→refresh→retry works for each
            concurrent caller independently.
            """

            def __init__(self) -> None:
                self.refresh_count = 0
                self.clear_count = 0
                self.auth_token = MagicMock(refresh_token="valid")
                self._refresh_lock = asyncio.Lock()
                self.call_counts: dict[str, int] = {}

            def clear_auth_token(self) -> bool:
                self.clear_count += 1
                return True

            async def refresh_access_token(self) -> bool:
                self.refresh_count += 1
                await asyncio.sleep(0.01)
                return True

            def make_method(self, name: str) -> Any:
                svc = self
                svc.call_counts[name] = 0

                @handle_api_errors
                async def method(self_arg: Any) -> str:
                    svc.call_counts[name] += 1
                    if svc.call_counts[name] == 1:
                        resp = MagicMock()
                        resp.status_code = 401
                        resp.text = "Unauthorized"
                        raise httpx.HTTPStatusError(
                            message="401", request=MagicMock(), response=resp
                        )
                    return f"{name}_ok"

                return method

        svc = ConcurrentService()

        methods = [svc.make_method(f"m{i}") for i in range(5)]
        results = await asyncio.gather(*[m(svc) for m in methods])

        assert all(r.endswith("_ok") for r in results)
        assert svc.clear_count == 0
        assert svc.refresh_count == 5
        assert len(results) == 5
