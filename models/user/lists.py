"""Request and response models for personal user lists."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

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
