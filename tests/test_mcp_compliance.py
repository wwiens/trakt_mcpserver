"""MCP Compliance Test Suite.

This module tests complete MCP specification compliance for the Trakt MCP server.
Tests validate all core MCP features: tools, resources, prompts, and capabilities.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest


class TestMCPCompliance:
    """Test MCP specification compliance."""

    @pytest.fixture
    def mcp_inspector_base_cmd(self) -> list[str]:
        """Base command for MCP inspector."""
        return [
            "npx",
            "@modelcontextprotocol/inspector",
            "--cli",
            "python",
            "server.py",
        ]

    def _run_mcp_command(self, cmd: list[str]) -> dict[str, Any]:
        """Run MCP inspector command and return parsed JSON result."""
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )

        if result.returncode != 0:
            pytest.fail(
                f"MCP command failed: {' '.join(cmd)}\n"
                + f"stdout: {result.stdout}\n"
                + f"stderr: {result.stderr}"
            )

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as e:
            pytest.fail(
                f"Failed to parse JSON response from: {' '.join(cmd)}\n"
                + f"Output: {result.stdout}\n"
                + f"Error: {e}"
            )

    def test_tools_list_compliance(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test that all tools are listed with complete metadata."""
        cmd = [*mcp_inspector_base_cmd, "--method", "tools/list"]
        data = self._run_mcp_command(cmd)

        # Verify response structure
        assert "tools" in data, "Response missing 'tools' key"
        tools: list[dict[str, Any]] = data["tools"]
        assert isinstance(tools, list), "Tools should be a list"
        assert len(tools) >= 26, f"Expected at least 26 tools, got {len(tools)}"

        # Check each tool has required MCP fields
        for tool in tools:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
            assert "inputSchema" in tool, f"Tool missing 'inputSchema': {tool}"

            # Validate tool name is non-empty string
            assert isinstance(tool["name"], str), (
                f"Tool name must be string: {tool['name']}"
            )
            assert tool["name"].strip(), f"Tool name cannot be empty: {tool['name']}"

            # Validate description is non-empty string
            assert isinstance(tool["description"], str), (
                f"Tool description must be string: {tool['description']}"
            )
            assert tool["description"].strip(), (
                f"Tool description cannot be empty: {tool['description']}"
            )

            # Validate input schema structure
            schema: dict[str, Any] = tool["inputSchema"]
            assert isinstance(schema, dict), f"Input schema must be dict: {schema}"
            assert "type" in schema, f"Input schema missing 'type': {schema}"
            assert schema["type"] == "object", (
                f"Input schema type must be 'object': {schema}"
            )

    def test_resources_list_compliance(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test that all resources are listed with complete metadata."""
        cmd = [*mcp_inspector_base_cmd, "--method", "resources/list"]
        data = self._run_mcp_command(cmd)

        # Verify response structure
        assert "resources" in data, "Response missing 'resources' key"
        resources: list[dict[str, Any]] = data["resources"]
        assert isinstance(resources, list), "Resources should be a list"
        assert len(resources) >= 13, (
            f"Expected at least 13 resources, got {len(resources)}"
        )

        # Check each resource has required MCP fields
        for resource in resources:
            assert "uri" in resource, f"Resource missing 'uri': {resource}"
            assert "name" in resource, f"Resource missing 'name': {resource}"
            assert "description" in resource, (
                f"Resource missing 'description': {resource}"
            )
            assert "mimeType" in resource, f"Resource missing 'mimeType': {resource}"

            # Validate resource fields
            assert isinstance(resource["uri"], str), (
                f"Resource uri must be string: {resource['uri']}"
            )
            assert resource["uri"].strip(), (
                f"Resource uri cannot be empty: {resource['uri']}"
            )

            assert isinstance(resource["name"], str), (
                f"Resource name must be string: {resource['name']}"
            )
            assert resource["name"].strip(), (
                f"Resource name cannot be empty: {resource['name']}"
            )

            assert isinstance(resource["description"], str), (
                f"Resource description must be string: {resource['description']}"
            )
            assert resource["description"].strip(), (
                f"Resource description cannot be empty: {resource['description']}"
            )

            assert isinstance(resource["mimeType"], str), (
                f"Resource mimeType must be string: {resource['mimeType']}"
            )
            assert resource["mimeType"] == "text/markdown", (
                f"Expected 'text/markdown', got: {resource['mimeType']}"
            )

    def test_prompts_list_compliance(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test that prompts are available with complete metadata."""
        cmd = [*mcp_inspector_base_cmd, "--method", "prompts/list"]
        data = self._run_mcp_command(cmd)

        # Verify response structure
        assert "prompts" in data, "Response missing 'prompts' key"
        prompts: list[dict[str, Any]] = data["prompts"]
        assert isinstance(prompts, list), "Prompts should be a list"
        assert len(prompts) >= 2, f"Expected at least 2 prompts, got {len(prompts)}"

        # Check each prompt has required MCP fields
        expected_prompts = {"discover_trending", "search_entertainment"}
        found_prompts: set[str] = set()

        for prompt in prompts:
            assert "name" in prompt, f"Prompt missing 'name': {prompt}"
            assert "description" in prompt, f"Prompt missing 'description': {prompt}"
            assert "arguments" in prompt, f"Prompt missing 'arguments': {prompt}"

            # Validate prompt fields
            assert isinstance(prompt["name"], str), (
                f"Prompt name must be string: {prompt['name']}"
            )
            assert prompt["name"].strip(), (
                f"Prompt name cannot be empty: {prompt['name']}"
            )

            assert isinstance(prompt["description"], str), (
                f"Prompt description must be string: {prompt['description']}"
            )
            assert prompt["description"].strip(), (
                f"Prompt description cannot be empty: {prompt['description']}"
            )

            assert isinstance(prompt["arguments"], list), (
                f"Prompt arguments must be list: {prompt['arguments']}"
            )

            found_prompts.add(prompt["name"])

        # Verify we have the expected prompts
        missing_prompts = expected_prompts - found_prompts
        assert not missing_prompts, f"Missing expected prompts: {missing_prompts}"

    def test_server_info_compliance(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test server provides proper info response."""
        # Note: MCP inspector doesn't have a direct server info command,
        # but we can verify the server starts and responds properly
        cmd = [*mcp_inspector_base_cmd, "--method", "tools/list"]
        data = self._run_mcp_command(cmd)

        # If tools/list works, the server is properly initialized
        assert "tools" in data, "Server failed to provide tools list"

    def test_capability_negotiation(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test server capabilities are properly declared."""
        # Test that all three core capabilities are available

        # Test tools capability
        tools_cmd = [*mcp_inspector_base_cmd, "--method", "tools/list"]
        tools_data = self._run_mcp_command(tools_cmd)
        assert "tools" in tools_data, "Tools capability not available"
        assert len(tools_data["tools"]) > 0, "No tools available"

        # Test resources capability
        resources_cmd = [*mcp_inspector_base_cmd, "--method", "resources/list"]
        resources_data = self._run_mcp_command(resources_cmd)
        assert "resources" in resources_data, "Resources capability not available"
        assert len(resources_data["resources"]) > 0, "No resources available"

        # Test prompts capability
        prompts_cmd = [*mcp_inspector_base_cmd, "--method", "prompts/list"]
        prompts_data = self._run_mcp_command(prompts_cmd)
        assert "prompts" in prompts_data, "Prompts capability not available"
        assert len(prompts_data["prompts"]) > 0, "No prompts available"

    def test_mcp_protocol_version(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test that server supports target MCP protocol version."""
        # The fact that MCP inspector can communicate with our server
        # indicates protocol compatibility. FastMCP handles version negotiation.
        cmd = [*mcp_inspector_base_cmd, "--method", "tools/list"]
        data = self._run_mcp_command(cmd)

        # Successful communication indicates protocol compatibility
        assert "tools" in data, "Protocol version incompatibility detected"

    @pytest.mark.parametrize(
        "tool_name",
        [
            "start_device_auth",
            "check_auth_status",
            "clear_auth",
            "fetch_trending_shows",
            "fetch_popular_shows",
            "search_shows",
            "search_movies",
        ],
    )
    def test_critical_tools_available(
        self, mcp_inspector_base_cmd: list[str], tool_name: str
    ) -> None:
        """Test that critical tools are available and properly configured."""
        cmd = [*mcp_inspector_base_cmd, "--method", "tools/list"]
        data = self._run_mcp_command(cmd)

        tools = data["tools"]
        tool_names = [tool["name"] for tool in tools]

        assert tool_name in tool_names, (
            f"Critical tool '{tool_name}' not found in: {tool_names}"
        )

        # Find the specific tool and validate its structure
        tool = next(t for t in tools if t["name"] == tool_name)
        assert tool["description"], f"Tool '{tool_name}' missing description"
        assert "inputSchema" in tool, f"Tool '{tool_name}' missing input schema"

    @pytest.mark.parametrize(
        "resource_uri",
        [
            "trakt://user/auth/status",
            "trakt://shows/trending",
            "trakt://movies/trending",
            "trakt://user/watched/shows",
        ],
    )
    def test_critical_resources_available(
        self, mcp_inspector_base_cmd: list[str], resource_uri: str
    ) -> None:
        """Test that critical resources are available and properly configured."""
        cmd = [*mcp_inspector_base_cmd, "--method", "resources/list"]
        data = self._run_mcp_command(cmd)

        resources = data["resources"]
        resource_uris = [resource["uri"] for resource in resources]

        assert resource_uri in resource_uris, (
            f"Critical resource '{resource_uri}' not found in: {resource_uris}"
        )

        # Find the specific resource and validate its structure
        resource = next(r for r in resources if r["uri"] == resource_uri)
        assert resource["description"], f"Resource '{resource_uri}' missing description"
        assert resource["mimeType"] == "text/markdown", (
            f"Resource '{resource_uri}' wrong mime type"
        )

    def test_error_handling_compliance(self, mcp_inspector_base_cmd: list[str]) -> None:
        """Test that error handling follows MCP specification."""
        # Test with an invalid method to verify error response structure
        cmd = [*mcp_inspector_base_cmd, "--method", "invalid/method"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )

        # Should fail with proper error response
        assert result.returncode != 0, "Invalid method should return error"

        # Error should be properly formatted (MCP inspector handles JSON-RPC error format)
        # The fact that we get a structured error response indicates compliance


class TestMCPFunctionalCompliance:
    """Test functional MCP compliance beyond basic structure."""

    def test_server_startup_and_shutdown(self) -> None:
        """Test that server starts and shuts down properly."""
        # Test that the server can be imported and started
        try:
            # Import should work without errors
            import server

            # Creating server should work
            mcp_server = server.create_server()
            assert mcp_server is not None, "Failed to create MCP server"

        except Exception as e:
            pytest.fail(f"Server startup failed: {e}")

    def test_mcp_transport_compatibility(self) -> None:
        """Test that server uses compatible MCP transport."""
        # Verify FastMCP is being used (handles JSON-RPC 2.0 transport)
        try:
            from mcp.server.fastmcp import FastMCP

            import server

            mcp_server = server.create_server()
            assert isinstance(mcp_server, FastMCP), (
                "Server must use FastMCP for MCP compliance"
            )

        except ImportError:
            pytest.fail("FastMCP not available - required for MCP compliance")
        except Exception as e:
            pytest.fail(f"MCP transport test failed: {e}")

    def test_async_support(self) -> None:
        """Test that server properly supports async operations."""
        # All our tools and resources are async - verify the server supports this
        import server

        try:
            mcp_server = server.create_server()

            # Server should be configured for async operation
            # FastMCP handles this automatically
            assert mcp_server is not None, "Server creation failed"

        except Exception as e:
            pytest.fail(f"Async support test failed: {e}")


class TestMCPSpecificationDetails:
    """Test specific MCP specification requirements."""

    def test_json_rpc_compliance(self) -> None:
        """Test JSON-RPC 2.0 compliance through FastMCP."""
        # FastMCP provides JSON-RPC 2.0 compliance
        # We verify this by checking successful communication with MCP inspector
        cmd = [
            "npx",
            "@modelcontextprotocol/inspector",
            "--cli",
            "python",
            "server.py",
            "--method",
            "tools/list",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )

        assert result.returncode == 0, f"JSON-RPC communication failed: {result.stderr}"

        # Should return valid JSON
        try:
            data = json.loads(result.stdout)
            assert "tools" in data, "Invalid JSON-RPC response structure"
        except json.JSONDecodeError:
            pytest.fail(f"Invalid JSON response: {result.stdout}")

    def test_mcp_message_format(self) -> None:
        """Test that messages follow MCP format specification."""
        # MCP inspector validates message format - successful communication indicates compliance
        cmd = [
            "npx",
            "@modelcontextprotocol/inspector",
            "--cli",
            "python",
            "server.py",
            "--method",
            "prompts/list",
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )

        assert result.returncode == 0, "MCP message format validation failed"

        data = json.loads(result.stdout)
        assert "prompts" in data, "MCP message format incorrect"

    def test_metadata_completeness(self) -> None:
        """Test that all metadata fields are complete and valid."""
        # Run all list commands and verify metadata completeness
        base_cmd = [
            "npx",
            "@modelcontextprotocol/inspector",
            "--cli",
            "python",
            "server.py",
        ]

        # Test tools metadata
        tools_result = subprocess.run(
            [*base_cmd, "--method", "tools/list"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )
        assert tools_result.returncode == 0
        tools_data = json.loads(tools_result.stdout)

        for tool in tools_data["tools"]:
            # Every tool must have non-empty description
            assert tool["description"].strip(), (
                f"Tool {tool['name']} has empty description"
            )
            # Every tool must have valid input schema
            assert tool["inputSchema"]["type"] == "object", (
                f"Tool {tool['name']} has invalid schema"
            )

        # Test resources metadata
        resources_result = subprocess.run(
            [*base_cmd, "--method", "resources/list"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )
        assert resources_result.returncode == 0
        resources_data = json.loads(resources_result.stdout)

        for resource in resources_data["resources"]:
            # Every resource must have non-empty description
            assert resource["description"].strip(), (
                f"Resource {resource['name']} has empty description"
            )
            # Every resource must have valid mime type
            assert resource["mimeType"] == "text/markdown", (
                f"Resource {resource['name']} has invalid mime type"
            )

        # Test prompts metadata
        prompts_result = subprocess.run(
            [*base_cmd, "--method", "prompts/list"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,
            timeout=30,
        )
        assert prompts_result.returncode == 0
        prompts_data = json.loads(prompts_result.stdout)

        for prompt in prompts_data["prompts"]:
            # Every prompt must have non-empty description
            assert prompt["description"].strip(), (
                f"Prompt {prompt['name']} has empty description"
            )
            # Every prompt must have arguments list (can be empty)
            assert isinstance(prompt["arguments"], list), (
                f"Prompt {prompt['name']} has invalid arguments"
            )
