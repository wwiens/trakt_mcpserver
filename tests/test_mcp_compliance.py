"""MCP Compliance Test Suite.

Tests complete MCP specification compliance for the Trakt MCP server using
the FastMCP CLI (``fastmcp inspect --format mcp``) — no Node dependency.
"""

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).parent.parent
SERVER_PATH = str(REPO_ROOT / "server.py")


@pytest.fixture(scope="module")
def mcp_report(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Any]:
    """Run ``fastmcp inspect --format mcp`` once, return parsed report.

    Writing to a file (``-o``) avoids interleaving with the server's startup
    logs that go to stdout.
    """
    report_path = tmp_path_factory.mktemp("mcp") / "report.json"
    result = subprocess.run(
        [
            "fastmcp",
            "inspect",
            SERVER_PATH,
            "--format",
            "mcp",
            "-o",
            str(report_path),
        ],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(
            f"fastmcp inspect failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return json.loads(report_path.read_text())


class TestMCPCompliance:
    """Test MCP specification compliance."""

    def test_tools_list_compliance(self, mcp_report: dict[str, Any]) -> None:
        """All tools are listed with complete metadata."""
        tools: list[dict[str, Any]] = mcp_report["tools"]
        assert isinstance(tools, list), "Tools should be a list"
        assert len(tools) >= 26, f"Expected at least 26 tools, got {len(tools)}"

        for tool in tools:
            assert "name" in tool, f"Tool missing 'name': {tool}"
            assert "description" in tool, f"Tool missing 'description': {tool}"
            assert "inputSchema" in tool, f"Tool missing 'inputSchema': {tool}"

            assert isinstance(tool["name"], str) and tool["name"].strip(), (
                f"Tool name must be non-empty string: {tool['name']}"
            )
            assert (
                isinstance(tool["description"], str) and tool["description"].strip()
            ), f"Tool description must be non-empty string: {tool['description']}"

            schema: dict[str, Any] = tool["inputSchema"]
            assert isinstance(schema, dict), f"Input schema must be dict: {schema}"
            assert schema.get("type") == "object", (
                f"Input schema type must be 'object': {schema}"
            )

    def test_resources_list_compliance(self, mcp_report: dict[str, Any]) -> None:
        """All resources are listed with complete metadata."""
        resources: list[dict[str, Any]] = mcp_report["resources"]
        assert isinstance(resources, list), "Resources should be a list"
        assert len(resources) >= 13, (
            f"Expected at least 13 resources, got {len(resources)}"
        )

        for resource in resources:
            for field in ("uri", "name", "description", "mimeType"):
                assert field in resource, f"Resource missing '{field}': {resource}"
                value = resource[field]
                assert isinstance(value, str) and value.strip(), (
                    f"Resource {field} must be non-empty string: {value}"
                )
            assert resource["mimeType"] == "text/markdown", (
                f"Expected 'text/markdown', got: {resource['mimeType']}"
            )

    def test_prompts_list_compliance(self, mcp_report: dict[str, Any]) -> None:
        """Prompts are available with complete metadata."""
        prompts: list[dict[str, Any]] = mcp_report["prompts"]
        assert isinstance(prompts, list), "Prompts should be a list"
        assert len(prompts) >= 2, f"Expected at least 2 prompts, got {len(prompts)}"

        expected_prompts = {"discover_trending", "search_entertainment"}
        found_prompts: set[str] = set()

        for prompt in prompts:
            for field in ("name", "description", "arguments"):
                assert field in prompt, f"Prompt missing '{field}': {prompt}"

            assert isinstance(prompt["name"], str) and prompt["name"].strip(), (
                f"Prompt name must be non-empty string: {prompt['name']}"
            )
            assert (
                isinstance(prompt["description"], str) and prompt["description"].strip()
            ), f"Prompt description must be non-empty string: {prompt['description']}"
            assert isinstance(prompt["arguments"], list), (
                f"Prompt arguments must be list: {prompt['arguments']}"
            )
            found_prompts.add(prompt["name"])

        missing = expected_prompts - found_prompts
        assert not missing, f"Missing expected prompts: {missing}"

    def test_server_info_compliance(self, mcp_report: dict[str, Any]) -> None:
        """Server reports identifying info."""
        info: dict[str, Any] = mcp_report["serverInfo"]
        assert info["name"] == "trakt-mcp-server", (
            f"Unexpected server name: {info['name']}"
        )
        assert isinstance(info["version"], str) and info["version"].strip(), (
            f"Server version must be non-empty string: {info['version']}"
        )

    def test_capability_negotiation(self, mcp_report: dict[str, Any]) -> None:
        """All three core capabilities declare non-empty lists."""
        assert mcp_report["tools"], "No tools available"
        assert mcp_report["resources"], "No resources available"
        assert mcp_report["prompts"], "No prompts available"

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
        self, mcp_report: dict[str, Any], tool_name: str
    ) -> None:
        """Critical tools are available and properly configured."""
        tools = mcp_report["tools"]
        tool = next((t for t in tools if t["name"] == tool_name), None)
        assert tool is not None, (
            f"Critical tool '{tool_name}' not found in: {[t['name'] for t in tools]}"
        )
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
        self, mcp_report: dict[str, Any], resource_uri: str
    ) -> None:
        """Critical resources are available and properly configured."""
        resources = mcp_report["resources"]
        resource = next((r for r in resources if r["uri"] == resource_uri), None)
        assert resource is not None, (
            f"Critical resource '{resource_uri}' not found in: "
            f"{[r['uri'] for r in resources]}"
        )
        assert resource["description"], f"Resource '{resource_uri}' missing description"
        assert resource["mimeType"] == "text/markdown", (
            f"Resource '{resource_uri}' wrong mime type"
        )

    def test_error_handling_compliance(self) -> None:
        """Invoking a non-existent tool returns a structured error."""
        result = subprocess.run(
            [
                "fastmcp",
                "call",
                SERVER_PATH,
                "definitely_not_a_real_tool",
            ],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            timeout=60,
        )
        assert result.returncode != 0, "Invalid tool should return error"


class TestToolAnnotationsAndTags:
    """Verify tool annotations and tags introduced by the FastMCP 3 gap closure."""

    def test_every_tool_has_tags(self, mcp_report: dict[str, Any]) -> None:
        """Every tool carries at least one tag (FastMCP _meta)."""
        untagged = [
            t["name"]
            for t in mcp_report["tools"]
            if not t.get("_meta", {}).get("fastmcp", {}).get("tags")
        ]
        assert not untagged, f"Tools missing tags: {untagged}"

    def test_annotations_populated_except_start_device_auth(
        self, mcp_report: dict[str, Any]
    ) -> None:
        """Only ``start_device_auth`` lacks annotations (deliberate, flow-starter)."""
        unannotated = [
            t["name"] for t in mcp_report["tools"] if t.get("annotations") is None
        ]
        assert unannotated == ["start_device_auth"], (
            f"Unexpected tools with null annotations: {unannotated}"
        )

    def test_all_write_tools_marked_destructive(
        self, mcp_report: dict[str, Any]
    ) -> None:
        """Every tool tagged ``write`` declares ``destructiveHint=True``."""
        for tool in mcp_report["tools"]:
            tags = tool.get("_meta", {}).get("fastmcp", {}).get("tags", [])
            if "write" in tags:
                ann: dict[str, Any] = tool.get("annotations") or {}
                assert ann.get("destructiveHint") is True, (
                    f"Write tool {tool['name']} missing destructiveHint=True"
                )

    def test_all_read_tools_marked_readonly(self, mcp_report: dict[str, Any]) -> None:
        """Every tool tagged ``read`` declares ``readOnlyHint=True``."""
        for tool in mcp_report["tools"]:
            tags = tool.get("_meta", {}).get("fastmcp", {}).get("tags", [])
            if "read" in tags:
                ann: dict[str, Any] = tool.get("annotations") or {}
                assert ann.get("readOnlyHint") is True, (
                    f"Read tool {tool['name']} missing readOnlyHint=True"
                )

    def test_auth_required_covers_writes_and_user_reads(
        self, mcp_report: dict[str, Any]
    ) -> None:
        """``auth_required`` tag covers every write (except ``clear_auth``) and
        every user-scoped read."""
        auth_required = {
            t["name"]
            for t in mcp_report["tools"]
            if "auth_required" in t.get("_meta", {}).get("fastmcp", {}).get("tags", [])
        }
        # All non-auth-flow writes
        expected_writes = {
            "add_to_history",
            "remove_from_history",
            "add_user_ratings",
            "remove_user_ratings",
            "add_user_watchlist",
            "remove_user_watchlist",
            "checkin_to_show",
            "hide_movie_recommendation",
            "hide_show_recommendation",
            "unhide_movie_recommendation",
            "unhide_show_recommendation",
            "remove_playback_item",
        }
        # User-scoped reads
        expected_reads = {
            "fetch_user_ratings",
            "fetch_user_watchlist",
            "fetch_history",
            "fetch_user_watched_shows",
            "fetch_user_watched_movies",
            "fetch_show_progress",
            "fetch_playback_progress",
            "fetch_movie_recommendations",
            "fetch_show_recommendations",
        }
        missing = (expected_writes | expected_reads) - auth_required
        assert not missing, f"Tools missing auth_required tag: {missing}"


class TestMCPFunctionalCompliance:
    """In-process functional compliance checks."""

    def test_server_startup(self) -> None:
        """Server module imports and ``create_server()`` returns a FastMCP instance."""
        from fastmcp import FastMCP

        import server

        mcp_server = server.create_server()
        assert isinstance(mcp_server, FastMCP), (
            "Server must use FastMCP for MCP compliance"
        )


class TestMCPSpecificationDetails:
    """Stricter per-item metadata checks (reads the same shared report)."""

    def test_metadata_completeness(self, mcp_report: dict[str, Any]) -> None:
        """Every tool/resource/prompt has complete, valid metadata."""
        for tool in mcp_report["tools"]:
            assert tool["description"].strip(), (
                f"Tool {tool['name']} has empty description"
            )
            assert tool["inputSchema"]["type"] == "object", (
                f"Tool {tool['name']} has invalid schema"
            )

        for resource in mcp_report["resources"]:
            assert resource["description"].strip(), (
                f"Resource {resource['name']} has empty description"
            )
            assert resource["mimeType"] == "text/markdown", (
                f"Resource {resource['name']} has invalid mime type"
            )

        for prompt in mcp_report["prompts"]:
            assert prompt["description"].strip(), (
                f"Prompt {prompt['name']} has empty description"
            )
            assert isinstance(prompt["arguments"], list), (
                f"Prompt {prompt['name']} has invalid arguments"
            )
