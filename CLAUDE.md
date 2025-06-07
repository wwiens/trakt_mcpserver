# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Model Context Protocol (MCP) server** that bridges AI language models with the Trakt.tv API for entertainment data access. The server is built using FastMCP and provides both public entertainment data and personal user data through OAuth authentication.

### Key Architecture Components

- **server.py**: Main MCP server with FastMCP decorators for resources and tools
- **trakt_client.py**: HTTP client for Trakt API interactions using httpx
- **models.py**: Pydantic models and data formatting utilities (FormatHelper class)
- **config.py**: Centralized configuration for API endpoints, MCP resources, and tool names
- **utils.py**: Error handling decorators and utility functions

### Authentication Flow

The project uses Trakt's OAuth device code flow:

1. Device code request generates user code and device code
2. User visits activation URL and enters code
3. Server polls token endpoint until user completes authorization
4. Token stored in `auth_token.json` for persistent authentication

## Development Commands

### Setup and Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up environment (copy and configure .env from .env.example)
cp .env.example .env
```

### Running and Testing
```bash
# Run the MCP server directly
python server.py

# Test with MCP Inspector (recommended for development)
mcp dev server.py

# Install in Claude Desktop
mcp install server.py

# Run all tests
pytest

# Run tests with verbose output
pytest -v -s

# Run specific test file
pytest tests/client/test_trakt_client.py -v

# Type checking with pyright
pyright

```

**Note:** Use `pytest.ini` configuration for async test support with `asyncio_default_fixture_loop_scope = session`.

### Testing Requirements

- **Always run tests after large changes** - Use `pytest` to ensure all tests pass before completing tasks
- **Run type checking** - Use `pyright` to verify type safety after code modifications
- **Test specific areas** - Run focused tests with `pytest tests/specific/test_file.py -v` when working on particular modules
- **Verify test count** - Ensure no tests are accidentally broken or removed during changes

## Code Quality Guidelines

### Type Hints
- Type hints are required for all functions, methods, and class attributes
- Use proper return type annotations including `None` where applicable
- Prefer specific types over generic ones (e.g., `list[str]` over `list`)
- Use `typing` module imports for complex types

### Function Design
- Functions must be focused and small - single responsibility principle
- Prefer pure functions without side effects where possible
- Use descriptive function and variable names

### Code Standards
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings for public functions and classes
- Keep line length under 88 characters (Black formatter standard)
- Prefer minimal inline comments that add value not obvious from the code
- Avoid commenting what the code does; comment why when context is needed

### Clean Code Principles
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions/classes
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **Fail Fast**: Validate inputs early and return clear error messages
- **Consistent Naming**: Use consistent patterns across the codebase
- **Small Functions**: Keep functions under 20 lines when possible
- **Avoid Deep Nesting**: Use early returns and guard clauses
- **Explicit is Better**: Prefer explicit imports and clear variable names over clever shortcuts

### Security Best Practices
- **Never hardcode secrets**: Use environment variables for API keys and sensitive data
- **Input Validation**: Validate all external inputs using Pydantic models
- **Error Handling**: Don't expose internal details in error messages to users
- **Authentication**: Always verify tokens before accessing user data
- **Logging Security**: Never log sensitive data (tokens, user IDs, personal info)
- **Dependency Security**: Keep dependencies updated and audit for vulnerabilities
- **File Permissions**: Ensure sensitive files like `auth_token.json` have proper permissions

## Code Architecture Notes

### MCP Resource vs Tool Pattern

- **Resources** (`@mcp.resource`) - Static data endpoints like trending shows, user watched history
- **Tools** (`@mcp.tool`) - Interactive functions with parameters like search, check-in, authentication

### Error Handling Strategy

- `@handle_api_errors` decorator in utils.py provides consistent API error handling
- All API methods return either structured data or error strings
- Authentication checks happen at tool/resource level, not client level

### Configuration Management

All endpoints, resource URIs, and tool names are centralized in `config.py`:

- `TRAKT_ENDPOINTS` - API endpoint paths
- `MCP_RESOURCES` - MCP resource URI patterns
- `TOOL_NAMES` - Consistent tool naming

### Data Flow

1. MCP tool/resource called → server.py handler
2. Handler creates TraktClient instance → trakt_client.py method
3. HTTP request to Trakt API with error handling
4. Response processed through Pydantic models
5. Data formatted via FormatHelper → markdown response

### Authentication Storage

- Tokens stored in `auth_token.json` at project root (gitignored)
- `TraktAuthToken` model handles token persistence and expiration
- Global `active_auth_flow` dict tracks ongoing device authorization
