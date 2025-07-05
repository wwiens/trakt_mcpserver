"""Main server module for the Trakt MCP server."""

import logging

from mcp.server.fastmcp import FastMCP

# Import all module registration functions
from .auth import register_auth_resources, register_auth_tools
from .checkin import register_checkin_tools
from .comments import register_comment_tools
from .movies import register_movie_resources, register_movie_tools
from .prompts.basic import register_basic_prompts
from .search import register_search_tools
from .shows import register_show_resources, register_show_tools
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

    # Register all modules
    register_auth_resources(mcp)
    register_auth_tools(mcp)

    register_show_resources(mcp)
    register_show_tools(mcp)

    register_movie_resources(mcp)
    register_movie_tools(mcp)

    register_comment_tools(mcp)

    register_user_resources(mcp)
    register_user_tools(mcp)

    register_search_tools(mcp)
    register_checkin_tools(mcp)

    register_basic_prompts(mcp)

    logger.info("All Trakt MCP modules registered successfully")
    return mcp


# Create the server instance
mcp = create_server()


if __name__ == "__main__":
    print("Starting Trakt MCP server...")
    print("Run 'mcp dev server.py' to test with the MCP Inspector")
    print("Run 'mcp install server.py' to install in Claude Desktop")
    mcp.run()
