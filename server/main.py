"""Main server module for the Trakt MCP server."""

import logging
import sys

from mcp.server.fastmcp import FastMCP

# Import all module registration functions
from .auth import register_auth_resources, register_auth_tools
from .checkin import register_checkin_tools
from .comments import register_comment_tools
from .movies import register_movie_resources, register_movie_tools
from .prompts.basic import register_basic_prompts
from .recommendations import register_recommendation_tools
from .search import register_search_tools
from .shows import register_show_resources, register_show_tools
from .sync import register_sync_tools
from .user import register_user_resources, register_user_tools

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trakt_mcp")


def create_server() -> FastMCP:
    """Create and configure the Trakt MCP server with all modules.

    Returns:
        Configured FastMCP server instance
    """
    # Create a named server with proper metadata for capability negotiation
    mcp = FastMCP(name="trakt-mcp-server")

    # Register all modules and capture handlers for type checker
    _ = register_auth_resources(mcp)
    _ = register_auth_tools(mcp)

    _ = register_show_resources(mcp)
    _ = register_show_tools(mcp)

    _ = register_movie_resources(mcp)
    _ = register_movie_tools(mcp)

    _ = register_comment_tools(mcp)

    _ = register_user_resources(mcp)
    _ = register_user_tools(mcp)

    _ = register_search_tools(mcp)
    _ = register_checkin_tools(mcp)
    _ = register_sync_tools(mcp)
    _ = register_recommendation_tools(mcp)

    # Register prompts and capture handlers for type checker
    _ = register_basic_prompts(mcp)

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
