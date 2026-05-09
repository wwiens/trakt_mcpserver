# Changelog

All notable changes to this project are documented in this file.
From v0.9.1 onward, entries are generated automatically by `python-semantic-release` from Conventional Commit messages.

<!-- version list -->

## v0.9.0 (2026-05-09)

First tagged release. Consolidates ~13 months of development into a tagged baseline ahead of the FastMCP 3 upgrade and tool consolidation milestones. Entries below summarize work delivered before automated changelog generation began.

### Features

- **Domains**: full coverage of shows, seasons, episodes, movies, people, comments, search, checkin, user, auth — each with focused HTTP clients, Pydantic models, and MCP tools/resources following single-responsibility layout (#10, #12, #34, #35, #37, #38).
- **Authentication**: OAuth device-code flow with persistent token storage, automatic 401 refresh-and-retry, and friendly error messages on auth failures (#32, #36, #40).
- **Discovery**: trending, popular, anticipated, related, and box-office surfaces for movies and shows; personalized recommendations with hide/unhide (#27, #30, #33, #34).
- **User data**: ratings management, watchlist management, watch history with progress tracking, comprehensive pagination (#19, #21, #23, #31).
- **Media metadata**: video support, summary endpoints for movies/shows (#12, #17).
- **Transports**: SSE (default) and stdio (#25); SSE image runs behind `mcp-proxy` for Docker deployments (#16).
- **Distribution**: multi-arch (amd64/arm64) Docker images auto-published to GHCR on every main push (#20).
- **Standards**: MCP protocol 2025-06-18 compliance (#11); pure single-responsibility architecture matching `trakt.apib` domain boundaries (#10).

### Bug Fixes

- Sync history reliability under partial-failure conditions (#42).
- Test isolation for auth tokens; 401 refresh-and-retry path coverage (#40, #43).
- Tool schema compliance with Trakt API field names (#28).
- Pagination behavior with `max_items` (#26).
- Strengthened error boundaries and unified status-code handling (#15).

### Code Quality

- Strict pyright type checking with maximum strictness rules (#7).
- Ruff for unified linting + formatting; E501 enforced project-wide (#8, #41).
- Multiple dedup/dead-code prune passes (#44, #45, #46).
- Formatter type safety overhaul (#39).

### Deprecations

- The bare `:stdio` Docker tag is preserved as an alias for `:latest-stdio` through the v0.9.x line. **It will be removed at v1.0.0** — update Docker pull commands to `:latest-stdio` (or pin a specific version like `:0.9.0-stdio`) before then.

### Notes

This entry is hand-curated. From v0.9.1 onward, every `feat:` / `fix:` / `perf:` / breaking commit on `main` automatically appends a section here.
