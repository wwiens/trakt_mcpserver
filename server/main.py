"""Main server module for the Trakt MCP server."""

import logging
import sys
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from typing import Final

from mcp.server.fastmcp import FastMCP

from client.pool import shutdown_clients

# Import all module registration functions
from .auth import register_auth_resources, register_auth_tools
from .checkin import register_checkin_tools
from .comments import register_comment_tools
from .episodes import register_episode_tools
from .movies import register_movie_resources, register_movie_tools
from .people import register_people_tools
from .progress import register_progress_tools
from .prompts.basic import register_basic_prompts
from .recommendations import register_recommendation_tools
from .search import register_search_tools
from .seasons import register_season_tools
from .shows import register_show_resources, register_show_tools
from .sync import register_sync_tools
from .user import register_user_resources, register_user_tools

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trakt_mcp")

REGISTRATIONS: Final[tuple[Callable[[FastMCP], object], ...]] = (
    register_auth_resources,
    register_auth_tools,
    register_show_resources,
    register_show_tools,
    register_movie_resources,
    register_movie_tools,
    register_comment_tools,
    register_user_resources,
    register_user_tools,
    register_search_tools,
    register_checkin_tools,
    register_sync_tools,
    register_progress_tools,
    register_recommendation_tools,
    register_season_tools,
    register_episode_tools,
    register_people_tools,
    register_basic_prompts,
)


@asynccontextmanager
async def _lifespan(_mcp: FastMCP) -> AsyncIterator[None]:
    """Close pooled HTTP clients when the server stops."""
    try:
        yield
    finally:
        await shutdown_clients()


def create_server() -> FastMCP:
    """Create and configure the Trakt MCP server with all modules.

    Returns:
        Configured FastMCP server instance
    """
    mcp = FastMCP(name="trakt-mcp-server", lifespan=_lifespan)
    for register in REGISTRATIONS:
        register(mcp)
    logger.info("All Trakt MCP modules registered successfully")
    return mcp


# Create the server instance
mcp = create_server()


if __name__ == "__main__":
    # Print to stderr to avoid polluting stdout (required for stdio transport)
    print("Starting Trakt MCP server...", file=sys.stderr)
    print("Run 'mcp dev server.py' to test with the MCP Inspector", file=sys.stderr)
    print("Run 'mcp install server.py' to install in Claude Desktop", file=sys.stderr)
    mcp.run()
