"""Pydantic models for Trakt recommendations."""

from typing import Annotated

from pydantic import BaseModel, Field


class UserIds(BaseModel):
    """User ID information."""

    slug: str | None = None


class RecommendationUser(BaseModel):
    """User information in a recommendation favorited_by entry."""

    username: str
    private: bool = False
    name: str | None = None
    vip: bool = False
    vip_ep: bool = False
    ids: UserIds = Field(default_factory=UserIds)


class FavoritedByEntry(BaseModel):
    """Entry in the favorited_by array of a recommendation."""

    user: RecommendationUser
    notes: str | None = None


class TraktRecommendedMovie(BaseModel):
    """Represents a recommended movie from Trakt API."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | None] = Field(
        description="Various IDs (trakt, slug, imdb, tmdb)"
    )
    favorited_by: Annotated[
        list[FavoritedByEntry],
        Field(
            default_factory=list,
            description="Users who favorited this recommendation",
        ),
    ]


class TraktRecommendedShow(BaseModel):
    """Represents a recommended show from Trakt API."""

    title: str
    year: int | None = None
    ids: dict[str, str | int | None] = Field(
        description="Various IDs (trakt, slug, tvdb, imdb, tmdb)"
    )
    favorited_by: Annotated[
        list[FavoritedByEntry],
        Field(
            default_factory=list,
            description="Users who favorited this recommendation",
        ),
    ]
