"""Base client for common HTTP functionality."""

import os
from typing import TYPE_CHECKING, Any, TypeVar, overload

import httpx
from dotenv import load_dotenv

from utils.api.errors import handle_api_errors

if TYPE_CHECKING:
    from models.auth import TraktAuthToken

T = TypeVar("T")


class BaseClient:
    """Base client with common HTTP functionality for Trakt API."""

    BASE_URL = "https://api.trakt.tv"

    def __init__(self):
        """Initialize the base client with credentials from environment variables."""
        load_dotenv()
        self.client_id = os.getenv("TRAKT_CLIENT_ID")
        self.client_secret = os.getenv("TRAKT_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise ValueError(
                "Trakt API credentials not found. Please check your .env file."
            )

        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }

        # Auth token will be set by subclasses
        self.auth_token: TraktAuthToken | None = None

    def _update_headers_with_token(self):
        """Update headers with authentication token."""
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token.access_token}"

    @handle_api_errors
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> Any:
        """Make an HTTP request to the Trakt API."""
        url = f"{self.BASE_URL}{endpoint}"

        async with httpx.AsyncClient() as client:
            if method.upper() == "GET":
                response = await client.get(url, headers=self.headers, params=params)
            elif method.upper() == "POST":
                response = await client.post(url, headers=self.headers, json=data)
            else:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data,
                    timeout=30.0,
                )
            response.raise_for_status()
            return response.json()

    async def _make_list_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Make a GET request that returns a list."""
        result = await self._make_request("GET", endpoint, params=params)
        # Type-check and return appropriate type
        if isinstance(result, list):
            return result  # type: ignore[return-value]
        raise ValueError(
            f"Expected list response from {endpoint}, got {type(result).__name__}: {result}"
        )

    async def _make_dict_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a GET request that returns a dictionary."""
        result = await self._make_request("GET", endpoint, params=params)
        # Type-check and return appropriate type
        if isinstance(result, dict):
            return result  # type: ignore[return-value]
        raise ValueError(
            f"Expected dict response from {endpoint}, got {type(result).__name__}: {result}"
        )

    async def _post_request(
        self,
        endpoint: str,
        data: dict[str, Any],
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request to the Trakt API."""
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        result = await self._make_request("POST", endpoint, data=data)
        # POST requests should return dict, not list
        if isinstance(result, dict):
            return result  # type: ignore[return-value]
        raise ValueError(
            f"Expected dict response from POST {endpoint}, got {type(result).__name__}: {result}"
        )

    @overload
    async def _make_typed_request(
        self,
        endpoint: str,
        *,
        response_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> T: ...

    @overload
    async def _make_typed_request(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]: ...

    async def _make_typed_request(
        self,
        endpoint: str,
        *,
        response_type: type[T] | None = None,
        params: dict[str, Any] | None = None,
    ) -> T | dict[str, Any]:
        """Make a typed GET request to the Trakt API.

        Returns the typed response if response_type is provided,
        otherwise returns the raw response data."""
        result = await self._make_request("GET", endpoint, params=params)
        # Runtime validation with response_type
        if response_type:
            if hasattr(response_type, "model_validate") and hasattr(
                response_type, "__annotations__"
            ):
                # Pydantic model - use model_validate for runtime validation
                return response_type.model_validate(result)  # type: ignore[attr-defined]
            # For non-Pydantic types, validate it's at least the expected base type
            if not isinstance(result, dict):
                raise ValueError(
                    f"Expected dict-like response for {response_type.__name__} from {endpoint}, "
                    + f"got {type(result).__name__}: {result}"
                )
            return result  # type: ignore[return-value]
        # If no response_type, ensure we return dict not list
        if isinstance(result, dict):
            return result  # type: ignore[return-value]
        raise ValueError(
            f"Expected dict response from {endpoint}, got {type(result).__name__}: {result}"
        )

    async def _make_typed_list_request(
        self,
        endpoint: str,
        *,
        response_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        """Make a typed GET request that returns a list."""
        result = await self._make_list_request(endpoint, params=params)
        # Runtime validation for list elements
        if hasattr(response_type, "model_validate") and hasattr(
            response_type, "__annotations__"
        ):
            # Pydantic model - validate each item
            return [response_type.model_validate(item) for item in result]  # type: ignore[attr-defined]
        # For non-Pydantic types, basic validation already done by _make_list_request
        # which ensures result is list[dict[str, Any]]
        return result  # type: ignore[return-value]
