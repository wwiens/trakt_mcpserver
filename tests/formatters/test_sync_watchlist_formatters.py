"""Tests for sync_watchlist formatters."""

from datetime import datetime

from models.formatters.sync_watchlist import SyncWatchlistFormatters
from models.movies.movie import TraktMovie
from models.shows.episode import TraktEpisode
from models.shows.show import TraktShow
from models.sync.watchlist import (
    SyncWatchlistNotFound,
    SyncWatchlistSummary,
    SyncWatchlistSummaryCount,
    TraktSeason,
    TraktSyncWatchlistItem,
    TraktWatchlistItem,
)
from models.types.pagination import PaginatedResponse, PaginationMetadata


class TestSyncWatchlistFormatters:
    """Tests for SyncWatchlistFormatters methods."""

    def test_format_user_watchlist_with_items(self) -> None:
        """Test formatting watchlist with items."""
        # Create sample watchlist items
        items = [
            create_movie_watchlist_item("Inception", 2010, 1, "2024-01-15", None),
            create_movie_watchlist_item(
                "The Matrix", 1999, 2, "2024-01-16", "Must watch on IMAX"
            ),
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=2
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Verify output
        assert "# Your Movies Watchlist (sorted by rank, asc)" in result
        assert (
            "2 total items" in result
        )  # Single page shows total items, not "Page 1 of 1"
        assert "Found 2 movies on this page:" in result
        assert "**Inception (2010)**" in result
        assert "rank #1" in result
        assert "added 2024-01-15" in result
        assert "**The Matrix (1999)**" in result
        assert "rank #2" in result
        assert "added 2024-01-16" in result
        assert "📝 **Note:** Must watch on IMAX" in result
        # Should not have navigation hints for single page
        assert "Navigation:" not in result

    def test_format_user_watchlist_empty(self) -> None:
        """Test formatting empty watchlist."""
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=0
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=[], pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Verify output
        assert "# Your Movies Watchlist" in result
        assert "Your movies watchlist is empty" in result
        assert "add_user_watchlist" in result
        assert (
            "0 total items" in result
        )  # Single page shows total items, not "Page 1 of 1"

    def test_format_user_watchlist_with_notes(self) -> None:
        """Test formatting watchlist with VIP notes."""
        items = [
            create_movie_watchlist_item(
                "Interstellar", 2014, 1, "2024-01-20", "Watch in 70mm IMAX"
            )
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=1
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Verify notes are displayed with VIP indicator
        assert "📝 **Note:** Watch in 70mm IMAX" in result

    def test_format_user_watchlist_pagination(self) -> None:
        """Test formatting watchlist with pagination navigation."""
        items = [create_movie_watchlist_item("Movie 1", 2020, 5, "2024-01-20", None)]
        pagination = PaginationMetadata(
            current_page=2, items_per_page=5, total_pages=4, total_items=18
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "added", "desc"
        )

        # Verify pagination info
        assert "Page 2 of 4" in result
        assert "18" in result  # total items
        assert "📍 **Navigation:**" in result
        assert "Previous: page 1" in result
        assert "Next: page 3" in result
        assert "sorted by added, desc" in result

    def test_format_user_watchlist_all_types(self) -> None:
        """Test formatting watchlist with all types grouped."""
        items = [
            create_movie_watchlist_item("Inception", 2010, 1, "2024-01-15", None),
            create_show_watchlist_item("Breaking Bad", 2008, 2, "2024-01-16", None),
            create_episode_watchlist_item(
                "Game of Thrones", 2011, 1, 5, 3, "2024-01-17", "Amazing episode!"
            ),
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=3
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "all", "rank", "asc"
        )

        # Verify grouping by type
        assert "# Your Watchlist Watchlist (sorted by rank, asc)" in result
        assert "## Episodes" in result
        assert "## Movies" in result
        assert "## Shows" in result
        # Verify items are present
        assert "**Inception (2010)**" in result
        assert "**Breaking Bad (2008)**" in result
        assert "**Game of Thrones - S01E05" in result
        assert "📝 **Note:** Amazing episode!" in result

    def test_format_user_watchlist_episodes(self) -> None:
        """Test formatting watchlist with episodes."""
        items = [
            create_episode_watchlist_item(
                "Breaking Bad", 2008, 1, 5, 1, "2024-01-15", "Season finale!"
            ),
            create_episode_watchlist_item(
                "Game of Thrones", 2011, 3, 9, 2, "2024-01-16", None
            ),
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=2
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "episodes", "rank", "asc"
        )

        # Verify episode formatting
        assert "Breaking Bad - S01E05" in result
        assert "Game of Thrones - S03E09" in result
        assert "📝 **Note:** Season finale!" in result

    def test_format_user_watchlist_seasons(self) -> None:
        """Test formatting watchlist with seasons."""
        items = [
            create_season_watchlist_item("Breaking Bad", 2008, 1, 1, "2024-01-15", None)
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=1
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "seasons", "rank", "asc"
        )

        # Verify season formatting
        assert "Breaking Bad - Season 1" in result

    def test_format_user_watchlist_summary_added(self) -> None:
        """Test formatting add operation summary."""
        summary = SyncWatchlistSummary(
            added=SyncWatchlistSummaryCount(movies=2, shows=1, seasons=0, episodes=0),
            existing=SyncWatchlistSummaryCount(
                movies=1, shows=0, seasons=0, episodes=0
            ),
            not_found=SyncWatchlistNotFound(
                movies=[
                    TraktSyncWatchlistItem(
                        title="Unknown Movie", year=2099, ids={"imdb": "tt9999999"}
                    )
                ],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", "movies"
        )

        # Verify output
        assert "# Watchlist Added - Movies" in result
        assert "✅ Successfully added **2** movies item(s)" in result
        assert "## Items Already in Watchlist (1)" in result
        assert "**1** movies item(s) were already in your watchlist" in result
        assert "## Items Not Found (1)" in result
        assert "Unknown Movie (2099)" in result

    def test_format_user_watchlist_summary_removed(self) -> None:
        """Test formatting remove operation summary."""
        summary = SyncWatchlistSummary(
            deleted=SyncWatchlistSummaryCount(movies=3, shows=2, seasons=1, episodes=0),
            not_found=SyncWatchlistNotFound(
                movies=[], shows=[], seasons=[], episodes=[]
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "removed", "movies"
        )

        # Verify output
        assert "# Watchlist Removed - Movies" in result
        assert "✅ Successfully removed **3** movies item(s)" in result
        # Should not show "Items Already in Watchlist" for remove operations
        assert "Items Already in Watchlist" not in result
        # Should not show "Items Not Found" if list is empty
        assert "Items Not Found" not in result

    def test_format_user_watchlist_summary_not_found(self) -> None:
        """Test formatting not found items in summary."""
        summary = SyncWatchlistSummary(
            added=SyncWatchlistSummaryCount(movies=0, shows=0, seasons=0, episodes=0),
            not_found=SyncWatchlistNotFound(
                movies=[
                    TraktSyncWatchlistItem(
                        title="Unknown Movie 1", year=2099, ids={"imdb": "tt1111111"}
                    ),
                    TraktSyncWatchlistItem(
                        title="Unknown Movie 2", year=2100, ids={"tmdb": "999999"}
                    ),
                ],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", "movies"
        )

        # Verify output
        assert "## Items Not Found (2)" in result
        assert "Unknown Movie 1 (2099)" in result
        assert "Unknown Movie 2 (2100)" in result
        assert "Please check the titles, years, and IDs for accuracy" in result

    def test_format_user_watchlist_summary_multiple_types(self) -> None:
        """Test formatting summary with multiple content types."""
        summary = SyncWatchlistSummary(
            added=SyncWatchlistSummaryCount(movies=5, shows=3, seasons=2, episodes=10),
            not_found=SyncWatchlistNotFound(
                movies=[], shows=[], seasons=[], episodes=[]
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", "movies"
        )

        # Verify breakdown by type is shown
        assert "### Breakdown by Type" in result
        assert "Movies: 5" in result
        assert "Shows: 3" in result
        assert "Seasons: 2" in result
        assert "Episodes: 10" in result

    def test_format_user_watchlist_summary_no_items(self) -> None:
        """Test formatting summary when no items were processed."""
        summary = SyncWatchlistSummary(
            added=SyncWatchlistSummaryCount(movies=0, shows=0, seasons=0, episodes=0),
            not_found=SyncWatchlistNotFound(
                movies=[], shows=[], seasons=[], episodes=[]
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", "movies"
        )

        # Verify output
        assert "No movies items were added" in result

    def test_format_user_watchlist_summary_not_found_ids_only(self) -> None:
        """Test formatting not found items with IDs but no title."""
        summary = SyncWatchlistSummary(
            added=SyncWatchlistSummaryCount(movies=0),
            not_found=SyncWatchlistNotFound(
                movies=[
                    TraktSyncWatchlistItem(ids={"imdb": "tt1234567", "tmdb": "12345"}),
                ],
                shows=[],
                seasons=[],
                episodes=[],
            ),
        )

        result = SyncWatchlistFormatters.format_user_watchlist_summary(
            summary, "added", "movies"
        )

        # Verify IDs are shown when no title available
        assert "## Items Not Found (1)" in result
        assert "imdb: tt1234567" in result or "tmdb: 12345" in result

    def test_format_user_watchlist_first_page(self) -> None:
        """Test formatting first page of watchlist."""
        items = [create_movie_watchlist_item("Movie 1", 2020, 1, "2024-01-20", None)]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=5, total_pages=3, total_items=15
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Should only show "Next" navigation
        assert "📍 **Navigation:**" in result
        assert "Next: page 2" in result
        assert "Previous:" not in result

    def test_format_user_watchlist_last_page(self) -> None:
        """Test formatting last page of watchlist."""
        items = [create_movie_watchlist_item("Movie 15", 2020, 15, "2024-01-20", None)]
        pagination = PaginationMetadata(
            current_page=3, items_per_page=5, total_pages=3, total_items=15
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Should only show "Previous" navigation
        assert "📍 **Navigation:**" in result
        assert "Previous: page 2" in result
        assert "Next:" not in result

    def test_format_user_watchlist_singularization(self) -> None:
        """Test correct singularization for single items."""
        items = [
            create_movie_watchlist_item("Single Movie", 2020, 1, "2024-01-20", None)
        ]
        pagination = PaginationMetadata(
            current_page=1, items_per_page=10, total_pages=1, total_items=1
        )
        paginated_response = PaginatedResponse[TraktWatchlistItem](
            data=items, pagination=pagination
        )

        result = SyncWatchlistFormatters.format_user_watchlist(
            paginated_response, "movies", "rank", "asc"
        )

        # Should use singular form "movie" not "movies"
        assert "Found 1 movie on this page:" in result


def create_movie_watchlist_item(
    title: str, year: int, rank: int, listed_date: str, notes: str | None
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for a movie."""
    movie = TraktMovie(
        title=title,
        year=year,
        ids={"trakt": str(rank), "slug": f"{title.lower().replace(' ', '-')}-{year}"},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=rank * 1000,
        listed_at=datetime.fromisoformat(f"{listed_date}T10:30:00.000+00:00"),
        notes=notes,
        type="movie",
        movie=movie,
    )


def create_show_watchlist_item(
    title: str, year: int, rank: int, listed_date: str, notes: str | None
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for a show."""
    show = TraktShow(
        title=title,
        year=year,
        ids={"trakt": str(rank), "slug": title.lower().replace(" ", "-")},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=rank * 1000,
        listed_at=datetime.fromisoformat(f"{listed_date}T10:30:00.000+00:00"),
        notes=notes,
        type="show",
        show=show,
    )


def create_episode_watchlist_item(
    show_title: str,
    show_year: int,
    season_number: int,
    episode_number: int,
    rank: int,
    listed_date: str,
    notes: str | None,
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for an episode."""
    show = TraktShow(
        title=show_title,
        year=show_year,
        ids={"trakt": str(rank), "slug": show_title.lower().replace(" ", "-")},
    )
    episode = TraktEpisode(
        season=season_number,
        number=episode_number,
        title=f"Episode {episode_number}",
        ids={"trakt": f"{rank}_{season_number}_{episode_number}"},
    )
    return TraktWatchlistItem(
        rank=rank,
        id=rank * 1000 + season_number * 100 + episode_number,
        listed_at=datetime.fromisoformat(f"{listed_date}T10:30:00.000+00:00"),
        notes=notes,
        type="episode",
        show=show,
        episode=episode,
    )


def create_season_watchlist_item(
    show_title: str,
    show_year: int,
    season_number: int,
    rank: int,
    listed_date: str,
    notes: str | None,
) -> TraktWatchlistItem:
    """Create a TraktWatchlistItem for a season."""
    show = TraktShow(
        title=show_title,
        year=show_year,
        ids={"trakt": str(rank), "slug": show_title.lower().replace(" ", "-")},
    )
    season = TraktSeason(number=season_number, ids={"trakt": f"{rank}_{season_number}"})
    return TraktWatchlistItem(
        rank=rank,
        id=rank * 1000 + season_number * 100,
        listed_at=datetime.fromisoformat(f"{listed_date}T10:30:00.000+00:00"),
        notes=notes,
        type="season",
        show=show,
        season=season,
    )
