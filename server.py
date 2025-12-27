# Backward compatibility - import from new modular structure
import sys

from server.main import mcp

if __name__ == "__main__":
    # Print to stderr to avoid polluting stdout (required for stdio transport)
    print("Starting Trakt MCP server...", file=sys.stderr)
    print("Run 'mcp dev server.py' to test with the MCP Inspector", file=sys.stderr)
    print("Run 'mcp install server.py' to install in Claude Desktop", file=sys.stderr)
    mcp.run()
