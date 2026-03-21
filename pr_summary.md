# feat: Add people domain with person summary, credits, and cast/crew tools

## Summary

Adds the **people domain** to the MCP server, providing person-level and per-title cast/crew tools that mirror the `/people` resource group in the Trakt API.

### New Tools (6)

| Tool | Description |
|------|-------------|
| `fetch_person_summary` | Person details with biography, social media, birthday (extended) or name/IDs only (basic) |
| `fetch_person_movies` | All movie credits for a person — cast roles and crew positions by department |
| `fetch_person_shows` | All show credits for a person — cast roles with episode counts and crew positions |
| `fetch_person_lists` | Lists containing a specific person, filterable by type and sort order |
| `fetch_movie_people` | Cast and crew for a specific movie |
| `fetch_show_people` | Cast and crew for a specific show, with optional guest stars |

### Architecture

Follows domain-isolation pattern established by seasons/episodes:

- **`client/people/`** — Full client with summary, movies, shows, and lists sub-clients + shared validation utilities
- **`client/movies/people.py`** / **`client/shows/people.py`** — Per-title people clients mixed into existing `MoviesClient` / `ShowsClient`
- **`server/people/tools.py`** — People tool handlers with `asyncio.gather` for parallel name + data fetching
- **`models/formatters/people.py`** — Person-centric formatters (bio, filmography, lists)
- **`models/formatters/movies.py`** / **`models/formatters/shows.py`** — Title-centric cast/crew formatters added to existing formatter classes
- **`models/types/api_responses.py`** — New TypedDict types: `PersonSocialIdsDict`, `PersonMovie*Credit`, `PersonShow*Credit`, `Person*CreditsResponse`
- **`config/endpoints/people.py`** — People endpoint templates (`/people/:id`, `/people/:id/movies`, etc.)

### Type Safety

- `fetch_person_lists` tool uses `Literal` types for `list_type` and `sort` parameters (consistent with `fetch_season_lists` / `fetch_episode_lists`)
- All new TypedDict types use `NotRequired` for optional API fields
- Pydantic `PersonIdParam` model with `field_validator` for input stripping/validation

### Test Coverage

- **Client tests**: `tests/client/people/` (summary, movies, shows, lists with validation edge cases), `tests/client/movies/test_people.py`, `tests/client/shows/test_people.py`
- **Server tests**: `tests/server/people/test_people_tools.py` (summary extended/basic/error, movies, shows, lists), plus `test_fetch_movie_people` and `test_fetch_show_people` / `test_fetch_show_people_with_guest_stars` added to existing movie/show test files
- All 1236 tests passing, ruff/pyright clean

### Files Changed

44 files changed, 2,184 insertions(+), 1 deletion(-)
