#!/usr/bin/env python3
"""Test script for the MCP server functionality."""

import asyncio
import json
from typing import Dict, Any

from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession
from mcp.client import types

from config import MCP_RESOURCES, TOOL_NAMES


async def test_resources(session: ClientSession):
    """Test MCP resources.
    
    Args:
        session: The MCP client session
    """
    print("\n=== Testing MCP Resources ===")
    
    # List available resources
    print("\nListing available resources...")
    resources = await session.list_resources()
    print(f"Found {len(resources)} resources:")
    for resource in resources:
        print(f"- {resource.uri}: {resource.description}")
    
    # Read trending shows resource
    print("\nReading trending shows resource...")
    trending_content, trending_mime = await session.read_resource(
        MCP_RESOURCES["shows_trending"],
        params={"limit": 3}
    )
    print(f"Mime type: {trending_mime}")
    print("Content:")
    print(trending_content[:500] + "..." if len(trending_content) > 500 else trending_content)
    
    # Read popular shows resource
    print("\nReading popular shows resource...")
    popular_content, popular_mime = await session.read_resource(
        MCP_RESOURCES["shows_popular"],
        params={"limit": 3}
    )
    print(f"Mime type: {popular_mime}")
    print("Content:")
    print(popular_content[:500] + "..." if len(popular_content) > 500 else popular_content)


async def test_tools(session: ClientSession):
    """Test MCP tools.
    
    Args:
        session: The MCP client session
    """
    print("\n=== Testing MCP Tools ===")
    
    # List available tools
    print("\nListing available tools...")
    tools = await session.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # Call trending shows tool
    print("\nCalling trending shows tool...")
    trending_result = await session.call_tool(
        TOOL_NAMES["fetch_trending_shows"],
        arguments={"limit": 3}
    )
    print("Result:")
    print(trending_result[:500] + "..." if len(trending_result) > 500 else trending_result)
    
    # Call popular shows tool
    print("\nCalling popular shows tool...")
    popular_result = await session.call_tool(
        TOOL_NAMES["fetch_popular_shows"],
        arguments={"limit": 3}
    )
    print("Result:")
    print(popular_result[:500] + "..." if len(popular_result) > 500 else popular_result)


async def run_tests():
    """Run all MCP tests."""
    server_params = types.ServerParams(
        app_info=types.ServerInfo(name="Test")
    )
    
    # Start the server process externally using:
    # $ python server.py
    
    print("Connecting to MCP server...")
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                print("Connected to server!")
                
                # Run tests
                await test_resources(session)
                await test_tools(session)
                
                print("\nTests completed successfully!")
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure the server is running with 'python server.py'")


if __name__ == "__main__":
    print("MCP Test Runner")
    print("===============")
    print("This script tests the MCP server functionality.")
    print("Make sure to run the server in a separate terminal with 'python server.py'")
    
    asyncio.run(run_tests()) 