"""Movie comments functionality."""

from typing import overload
from urllib.parse import quote

from config.api import DEFAULT_LIMIT, DEFAULT_MAX_PAGES
from config.endpoints import TRAKT_ENDPOINTS
from models.types import CommentResponse
from models.types.pagination import PaginatedResponse
from models.types.sort import MovieCommentSort
from utils.api.errors import handle_api_errors

from ..base import BaseClient


class MovieCommentsClient(BaseClient):
    """Client for movie comments operations."""

    @overload
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: None = None,
        sort: MovieCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse]: ...

    @overload
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int = ...,
        sort: MovieCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> PaginatedResponse[CommentResponse]: ...

    @handle_api_errors
    async def get_movie_comments(
        self,
        movie_id: str,
        limit: int = DEFAULT_LIMIT,
        page: int | None = None,
        sort: MovieCommentSort = "newest",
        max_pages: int = DEFAULT_MAX_PAGES,
    ) -> list[CommentResponse] | PaginatedResponse[CommentResponse]:
        """Get comments for a movie.

        Args:
            movie_id: The Trakt movie ID
            sort: Sort order for comments

        See ``BaseClient._fetch_paginated`` for pagination semantics.
        """
        endpoint = (
            TRAKT_ENDPOINTS["comments_movie"]
            .replace(":id", quote(movie_id, safe=""))
            .replace(":sort", sort)
        )

        return await self._fetch_paginated(
            endpoint,
            response_type=CommentResponse,
            page=page,
            limit=limit,
            max_pages=max_pages,
        )
