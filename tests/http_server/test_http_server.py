#!/usr/bin/env python3
"""Test script for the Trakt MCP HTTP server."""

import requests
import sys
from typing import Optional

def test_server(base_url: str = "http://localhost:8000") -> bool:
    """Test the MCP server endpoints.

    Args:
        base_url: The base URL of the server to test.
    Returns:
        True if all tests pass, False otherwise.
    """
    print(f"Testing Trakt MCP server at {base_url}")
    print("=" * 50)

    # Test health endpoint
    print("1. Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ Root endpoint working")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")

    # Test tools endpoint
    print("\n3. Testing tools endpoint...")
    try:
        response = requests.get(f"{base_url}/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print("✅ Tools endpoint working")
            print(f"   Available tools: {len(tools.get('tools', []))}")
            for tool in tools.get('tools', [])[:3]:  # Show first 3 tools
                print(f"   - {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        else:
            print(f"❌ Tools endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Tools endpoint error: {e}")

    # Test resources endpoint
    print("\n4. Testing resources endpoint...")
    try:
        response = requests.get(f"{base_url}/resources", timeout=5)
        if response.status_code == 200:
            resources = response.json()
            print("✅ Resources endpoint working")
            print(f"   Available resources: {len(resources.get('resources', []))}")
            for resource in resources.get('resources', [])[:3]:  # Show first 3 resources
                print(f"   - {resource.get('name', 'Unknown')}: {resource.get('description', 'No description')}")
        else:
            print(f"❌ Resources endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Resources endpoint error: {e}")

    # Test MCP initialize
    print("\n5. Testing MCP initialize...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }
        response = requests.post(f"{base_url}/mcp", json=mcp_request, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ MCP initialize working")
            print(f"   Server: {result.get('result', {}).get('serverInfo', {})}")
        else:
            print(f"❌ MCP initialize failed: {response.status_code}")
    except Exception as e:
        print(f"❌ MCP initialize error: {e}")

    print("\n" + "=" * 50)
    print("✅ Server test completed successfully!")
    return True

if __name__ == "__main__":
    # Get base URL from command line argument or use default
    base_url: str = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    success: bool = test_server(base_url)
    sys.exit(0 if success else 1) 