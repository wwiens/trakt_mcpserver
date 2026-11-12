"""Request and response models for personal user lists."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow
from models.sync.watchlist import TraktSeason
from models.types.ids import TraktIds

ListPrivacy = Literal["private", "link", "friends", "public"]
ListSortBy = Literal[
    "rank",
    "added",
    "title",
    "released",
    "runtime",
    "popularity",
    "random",
    "percentage",
    "imdb_rating",
    "tmdb_rating",
    "rt_tomatometer",
    "rt_audience",
    "metascore",
    "votes",
    "imdb_votes",
    "tmdb_votes",
    "my_rating",
    "watched",
    "collected",
]
ListSortHow = Literal["asc", "desc"]
UserListItemType = Literal["movie", "show", "season", "episode", "person"]


class UserListFields(BaseModel):
    """Optional fields shared by list creation and updates."""

    description: str | None = None
    privacy: ListPrivacy | None = None
    display_numbers: bool | None = None
    allow_comments: bool | None = None
    sort_by: ListSortBy | None = None
    sort_how: ListSortHow | None = None


class CreateUserList(UserListFields):
    """Create a personal list, leaving omitted defaults to Trakt."""

    name: str = Field(min_length=1)


class UpdateUserList(UserListFields):
    """Update at least one field without overwriting omitted settings."""

    name: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def require_changes(self) -> "UpdateUserList":
        """Reject updates with no non-null fields."""
        if not self.model_dump(exclude_none=True):
            raise ValueError("Provide at least one field to update")
        return self


class UserListIds(BaseModel):
    """Stable Trakt list identifier and slug."""

    trakt: int
    slug: str


class UserList(BaseModel):
    """Personal list metadata returned by Trakt."""

    name: str
    description: str | None = None
    privacy: ListPrivacy
    item_count: int = Field(ge=0)
    ids: UserListIds


class UserListPerson(BaseModel):
    """Person identity within a personal list item."""

    name: str
    ids: TraktIds


class UserListItem(BaseModel):
    """Personal list entry, distinct from the underlying media's Trakt ID."""

    rank: int = Field(ge=1)
    id: int = Field(ge=1)
    listed_at: datetime
    notes: str | None = None
    type: UserListItemType
    movie: TraktMovie | None = None
    show: TraktShow | None = None
    season: TraktSeason | None = None
    episode: TraktEpisode | None = None
    person: UserListPerson | None = None
