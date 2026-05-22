"""Modular Trakt MCP server."""

# Load .env before any submodule import, so module-level env reads
# (e.g. AUTH_TOKEN_FILE in client.auth.client) see the file's values.
from dotenv import load_dotenv

load_dotenv()

from .main import create_server, mcp  # noqa: E402

__all__ = [
    "create_server",
    "mcp",
]
