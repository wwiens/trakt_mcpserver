"""Base client for common HTTP functionality."""

import os
from typing import TYPE_CHECKING, Any, Protocol, TypeGuard, TypeVar, overload

import httpx
from dotenv import load_dotenv

from models.types.pagination import PaginatedResponse, PaginationMetadata
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
    return isinstance(result, list) and all(isinstance(item, dict) for item in result)  # type: ignore[reportUnknownVariableType] # Runtime type guard validation


def _is_pydantic_model(cls: type[object]) -> TypeGuard[type[PydanticModel]]:
    """Type guard for Pydantic models."""
    return hasattr(cls, "model_validate") and hasattr(cls, "__annotations__")


class BaseClient:
    """Base client with common HTTP functionality for Trakt API."""

    BASE_URL = "https://api.trakt.tv"
    REQUEST_TIMEOUT = 30.0

    def __init__(self):
        """Initialize the base client with credentials from environment variables."""
        load_dotenv()
        client_id = os.getenv("TRAKT_CLIENT_ID")
        client_secret = os.getenv("TRAKT_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "Trakt API credentials not found. Please check your .env file."
            )

        self.client_id: str = client_id
        self.client_secret: str = client_secret
        self.headers: dict[str, str] = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }

        self.auth_token: TraktAuthToken | None = None
        self._client: httpx.AsyncClient | None = None

    def _update_headers_with_token(self):
        """Update headers with authentication token."""
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token.access_token}"

    async def __aenter__(self) -> "BaseClient":
        """Enter async context and initialize shared client."""
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL, timeout=self.REQUEST_TIMEOUT
        )
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit async context and close shared client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create shared HTTP client.

        Returns existing client if available, otherwise creates temporary client
        for backward compatibility with non-context-manager usage.
        """
        if self._client:
            return self._client
        # Fallback for non-context-manager usage (backward compatibility)
        return httpx.AsyncClient(base_url=self.BASE_URL, timeout=self.REQUEST_TIMEOUT)

    def _extract_pagination_headers(
        self, response: "httpx.Response"
    ) -> PaginationMetadata:
        """Extract pagination metadata from Trakt API response headers.

        Maps X-Pagination-* headers to PaginationMetadata model.

        Args:
            response: HTTP response with pagination headers

        Returns:
            PaginationMetadata with current page info

        Raises:
            ValueError: If required pagination headers are missing or invalid
        """
        try:
            current_page = int(response.headers.get("X-Pagination-Page", "1"))
            items_per_page = int(response.headers.get("X-Pagination-Limit", "10"))
            total_pages = int(response.headers.get("X-Pagination-Page-Count", "1"))
            total_items = int(response.headers.get("X-Pagination-Item-Count", "0"))

            return PaginationMetadata(
                current_page=current_page,
                items_per_page=items_per_page,
                total_pages=total_pages,
                total_items=total_items,
            )
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid pagination headers in response: {e}") from e

    @handle_api_errors
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Make an HTTP request to the Trakt API."""
        # Ensure Authorization header is present when authenticated
        self._update_headers_with_token()
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        client = self._get_client()
        should_close = self._client is None  # Only close if temporary client

        try:
            if method.upper() == "GET":
                response = await client.get(
                    endpoint,
                    headers=request_headers,
                    params=params,
                    timeout=self.REQUEST_TIMEOUT,
                )
            elif method.upper() == "POST":
                response = await client.post(
                    endpoint,
                    headers=request_headers,
                    json=data,
                    timeout=self.REQUEST_TIMEOUT,
                )
            else:
                response = await client.request(
                    method=method,
                    url=endpoint,
                    headers=request_headers,
                    params=params,
                    json=data,
                    timeout=self.REQUEST_TIMEOUT,
                )
            response.raise_for_status()
            return response.json()
        finally:
            if should_close:
                await client.aclose()

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
        result = await self._make_request("POST", endpoint, data=data, headers=headers)
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

    @handle_api_errors
    async def _make_paginated_request(
        self,
        endpoint: str,
        *,
        response_type: type[T],
        params: dict[str, Any] | None = None,
    ) -> PaginatedResponse[T]:  # type: ignore[return] # Complex generic typing with TypedDict compatibility
        """Make a paginated GET request to the Trakt API.

        Returns both the data and pagination metadata from response headers.

        Args:
            endpoint: API endpoint to call
            response_type: Type for individual items in the response
            params: Optional query parameters including page/limit

        Returns:
            PaginatedResponse with data and pagination metadata

        Raises:
            ValueError: If response format is invalid or headers missing
        """
        # Ensure Authorization header is present when authenticated
        self._update_headers_with_token()
        request_headers = self.headers

        client = self._get_client()
        should_close = self._client is None  # Only close if temporary client

        try:
            response = await client.get(
                endpoint,
                headers=request_headers,
                params=params,
                timeout=self.REQUEST_TIMEOUT,
            )
            response.raise_for_status()

            # Parse response data first to get actual item count
            result = response.json()
            if not _is_list_response(result):
                raise ValueError(
                    f"Expected list response for paginated request to {endpoint}, "
                    + f"got {type(result).__name__}: {result}"
                )

            # Convert to typed objects if Pydantic model
            if _is_pydantic_model(response_type):
                typed_data = [response_type.model_validate(item) for item in result]
            else:
                typed_data = result  # type: ignore[assignment] # TypedDict runtime limitation

            # Extract pagination metadata from headers
            try:
                pagination = self._extract_pagination_headers(response)
            except ValueError as e:
                # Convert to an exception type that will be handled by @handle_api_errors
                raise RuntimeError(f"Failed to parse pagination headers: {e}") from e

            # Fix total_items when no pagination headers present (non-paginated requests)
            if pagination.total_items == 0 and len(typed_data) > 0:
                pagination = PaginationMetadata(
                    current_page=pagination.current_page,
                    items_per_page=len(typed_data),  # All items on single page
                    total_pages=1,  # Single page with all items
                    total_items=len(typed_data),  # Actual count of items
                )

            return PaginatedResponse(  # type: ignore[return-value] # Generic type compatibility
                data=typed_data,
                pagination=pagination,
            )
        finally:
            if should_close:
                await client.aclose()

    async def auto_paginate(
        self,
        endpoint: str,
        *,
        response_type: type[T],
        params: dict[str, Any] | None = None,
        max_pages: int = 100,
    ) -> list[T]:
        """Auto-paginate through all pages of a paginated endpoint.

        Fetches all pages by iterating using server-provided next_page.
        Includes safety cap to prevent runaway loops.

        Args:
            endpoint: API endpoint to paginate
            response_type: Type for individual items in response
            params: Base query parameters (page will be added/overridden)
            max_pages: Maximum number of pages to fetch (safety guard, default: 100)

        Returns:
            List of all items across all pages (up to max_pages)

        Raises:
            RuntimeError: If max_pages reached without natural pagination end
        """
        all_items: list[T] = []
        current_page = 1
        base_params = params or {}

        for _ in range(1, max_pages + 1):
            # Merge base params with current page
            page_params = {**base_params, "page": current_page}

            response = await self._make_paginated_request(
                endpoint,
                response_type=response_type,
                params=page_params,
            )

            all_items.extend(response.data)

            # Use server-provided next_page instead of manual increment
            next_page = response.pagination.next_page()
            if next_page is None:
                break

            current_page = next_page
        else:
            # Loop completed without break - hit max_pages limit
            raise RuntimeError(
                f"Pagination safety limit reached: {max_pages} pages fetched. "
                + "Consider using explicit page parameter or increasing max_pages."
            )

        return all_items

    @overload
    async def _post_typed_request(
        self,
        endpoint: str,
        data: dict[str, Any],
        *,
        response_type: type[T],
        headers: dict[str, str] | None = None,
    ) -> T: ...

    @overload
    async def _post_typed_request(
        self,
        endpoint: str,
        data: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]: ...

    async def _post_typed_request(
        self,
        endpoint: str,
        data: dict[str, Any],
        *,
        response_type: type[T] | None = None,
        headers: dict[str, str] | None = None,
    ) -> T | dict[str, Any]:
        """Make a typed POST request to the Trakt API.

        Returns the typed response if response_type is provided,
        otherwise returns the raw response data."""
        result = await self._post_request(endpoint, data, headers=headers)

        if response_type is None:
            return result

        if _is_pydantic_model(response_type):
            return response_type.model_validate(result)

        return result  # type: ignore[return-value] # TypedDict runtime limitation
