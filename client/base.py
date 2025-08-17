"""Base client for common HTTP functionality."""

import os
from typing import TYPE_CHECKING, Any, Protocol, TypeGuard, TypeVar, overload

import httpx
from dotenv import load_dotenv

from utils.api.errors import handle_api_errors

if TYPE_CHECKING:
    from models.auth import TraktAuthToken

T = TypeVar("T")


class PydanticModel(Protocol):
    """Protocol for Pydantic models."""

    @classmethod
    def model_validate(cls, obj: Any) -> Any: ...


def _is_dict_response(result: Any) -> TypeGuard[dict[str, Any]]:
    """Type guard for dict responses."""
    return isinstance(result, dict)


def _is_list_response(result: Any) -> TypeGuard[list[dict[str, Any]]]:
    """Type guard for list responses."""
    return isinstance(result, list)


def _is_pydantic_model(cls: type[T]) -> TypeGuard[type[PydanticModel]]:
    """Type guard for Pydantic models."""
    return hasattr(cls, "model_validate") and hasattr(cls, "__annotations__")


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
        if _is_list_response(result):
            return result
        raise ValueError(
            f"Expected list response from {endpoint}, got {type(result).__name__}: {result}"
        )

    async def _make_dict_request(
        self, endpoint: str, params: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make a GET request that returns a dictionary."""
        result = await self._make_request("GET", endpoint, params=params)
        if _is_dict_response(result):
            return result
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
        if _is_dict_response(result):
            return result
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

        if response_type is None:
            if _is_dict_response(result):
                return result
            raise ValueError(
                f"Expected dict response from {endpoint}, got {type(result).__name__}: {result}"
            )

        if _is_pydantic_model(response_type):
            return response_type.model_validate(result)

        if not _is_dict_response(result):
            raise ValueError(
                f"Expected dict-like response for {response_type.__name__} from {endpoint}, "
                + f"got {type(result).__name__}: {result}"
            )

        return result  # type: ignore[return-value] # TypedDict runtime limitation

    async def _make_typed_list_request(
        self,
        endpoint: str,
        *,
        response_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> list[T]:
        """Make a typed GET request that returns a list."""
        result = await self._make_list_request(endpoint, params=params)
        if _is_pydantic_model(response_type):
            return [response_type.model_validate(item) for item in result]
        return result  # type: ignore[return-value] # TypedDict runtime limitation
