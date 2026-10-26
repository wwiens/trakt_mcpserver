# Changelog

All notable changes to this project are documented in this file.
From v0.9.1 onward, entries are generated automatically by `python-semantic-release` from Conventional Commit messages.

<!-- version list -->

## v0.11.1 (2026-10-26)

### Bug Fixes

- Empty pagination limit (#66) ([#66](https://github.com/wwiens/trakt_mcpserver/pull/66),
  [`88ee070`](https://github.com/wwiens/trakt_mcpserver/commit/88ee070977e1cb450a9e65dc70f0223e0b66d365))

### Continuous Integration

- Publish to PyPI from release workflow (#65)
  ([#65](https://github.com/wwiens/trakt_mcpserver/pull/65),
  [`1de672c`](https://github.com/wwiens/trakt_mcpserver/commit/1de672caa09f43039d5352cdd0e3c7e1813384bd))


## v0.11.0 (2026-10-25)

### Build System

- Declare MIT license in package and image metadata (#62)
  ([#62](https://github.com/wwiens/trakt_mcpserver/pull/62),
  [`0c8e5b5`](https://github.com/wwiens/trakt_mcpserver/commit/0c8e5b5524536bf7bd3c54882fb9836ad9ddf3c7))

- **deps-dev**: Upgrade and pin pyright to 1.1.411 (#59)
  ([#59](https://github.com/wwiens/trakt_mcpserver/pull/59),
  [`f38936d`](https://github.com/wwiens/trakt_mcpserver/commit/f38936dac59639849409d24cfe0aed9b1782352a))

### Continuous Integration

- Auto-label PRs by conventional commit title and file paths (#56)
  ([#56](https://github.com/wwiens/trakt_mcpserver/pull/56),
  [`4ea76af`](https://github.com/wwiens/trakt_mcpserver/commit/4ea76af3dcfec65eb43ebd9d30dadc0a2cb04d11))

- Publish to PyPI on GitHub Release (#52) ([#52](https://github.com/wwiens/trakt_mcpserver/pull/52),
  [`6bec169`](https://github.com/wwiens/trakt_mcpserver/commit/6bec169c9d20e15068da5f842c1e1bf76dc9271e))

- SHA-pin third-party actions (#53) ([#53](https://github.com/wwiens/trakt_mcpserver/pull/53),
  [`abbfc7f`](https://github.com/wwiens/trakt_mcpserver/commit/abbfc7fed03fe0c9d4a169efea64231230a7d702))

### Documentation

- Add the MIT LICENSE file the README links to (#61)
  ([#61](https://github.com/wwiens/trakt_mcpserver/pull/61),
  [`4763df0`](https://github.com/wwiens/trakt_mcpserver/commit/4763df07e822890c7fa897fa6c5156fa9f8dccf0))

### Features

- Auth host migration (#64) ([#64](https://github.com/wwiens/trakt_mcpserver/pull/64),
  [`d477b39`](https://github.com/wwiens/trakt_mcpserver/commit/d477b391218065228117b3a9e77e9a2ebdd13de4))

### Refactoring

- Codeql dead code cleanup (#54) ([#54](https://github.com/wwiens/trakt_mcpserver/pull/54),
  [`7ab6c4d`](https://github.com/wwiens/trakt_mcpserver/commit/7ab6c4df70741f12af9432148a5c75436f565c88))


## v0.10.0 (2026-05-22)

### Continuous Integration

- Add quality gates (#50) ([#50](https://github.com/wwiens/trakt_mcpserver/pull/50),
  [`09fde32`](https://github.com/wwiens/trakt_mcpserver/commit/09fde32a81f05af7170b5d22ef66425dd6b4916a))

### Documentation

- Recommend venv before pip install -e . (#48)
  ([#48](https://github.com/wwiens/trakt_mcpserver/pull/48),
  [`ed0fd16`](https://github.com/wwiens/trakt_mcpserver/commit/ed0fd165fc1a500408e3cdf0f9d8e3d51e625472))

### Features

- Add uvx install option (#51) ([#51](https://github.com/wwiens/trakt_mcpserver/pull/51),
  [`1a3ff31`](https://github.com/wwiens/trakt_mcpserver/commit/1a3ff3188d28a6c21fc86b401bbf2dc6abf6c0e9))


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
