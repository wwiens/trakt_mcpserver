# Backward compatibility - import from new modular structure
from server.main import mcp

if __name__ == "__main__":
    print("Starting Trakt MCP server...")
    print("Run 'mcp dev server.py' to test with the MCP Inspector")
    print("Run 'mcp install server.py' to install in Claude Desktop")
    mcp.run()
