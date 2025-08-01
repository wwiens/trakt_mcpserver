#!/usr/bin/env python3
"""Tests for the MCP endpoint to ensure n8n compatibility."""

import json
import pytest
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from fastapi import FastAPI

from server.http_server import app


class TestMCPEndpoint:
    """Test the /mcp endpoint for n8n compatibility."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    @pytest.fixture
    def valid_mcp_request(self) -> Dict[str, Any]:
        """Create a valid MCP request."""
        return {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {}
        }

    def test_mcp_endpoint_initialize_success(self, client, valid_mcp_request):
        """Test successful MCP initialize method."""
        response = client.post("/mcp", json=valid_mcp_request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 1
        assert "result" in data
        
        # Check server info
        result = data["result"]
        assert "serverInfo" in result
        server_info = result["serverInfo"]
        assert "service" in server_info
        assert "version" in server_info
        assert server_info["service"] == "Trakt MCP Server"

    def test_mcp_endpoint_tools_list_success(self, client):
        """Test successful MCP tools/list method."""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 2
        assert "result" in data
        
        # Check tools structure
        result = data["result"]
        assert "tools" in result
        tools = result["tools"]
        assert isinstance(tools, list)
        
        # Check each tool has required fields for n8n
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # n8n requires inputSchema to be a valid JSON Schema
            input_schema = tool["inputSchema"]
            assert isinstance(input_schema, dict)
            assert "type" in input_schema
            assert input_schema["type"] == "object"

    def test_mcp_endpoint_resources_list_success(self, client):
        """Test successful MCP resources/list method."""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "resources/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 3
        assert "result" in data
        
        # Check resources structure
        result = data["result"]
        assert "resources" in result
        resources = result["resources"]
        assert isinstance(resources, list)
        
        # Check each resource has required fields
        for resource in resources:
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource

    def test_mcp_endpoint_resources_read_success(self, client):
        """Test successful MCP resources/read method."""
        request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/read",
            "params": {
                "uri": "trakt://shows/trending"
            }
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 compliance
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 4
        assert "result" in data
        
        # Check content structure
        result = data["result"]
        assert "contents" in result
        contents = result["contents"]
        assert isinstance(contents, list)
        
        # Check each content has required fields
        for content in contents:
            assert "uri" in content
            assert "mimeType" in content
            assert "text" in content

    def test_mcp_endpoint_missing_method(self, client):
        """Test MCP endpoint with missing method."""
        request = {
            "jsonrpc": "2.0",
            "id": 5,
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Missing method" in data["detail"]

    def test_mcp_endpoint_invalid_method(self, client):
        """Test MCP endpoint with invalid method."""
        request = {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "invalid/method",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 error format
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 6
        assert "error" in data
        
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == -32601  # Method not found

    def test_mcp_endpoint_malformed_json(self, client):
        """Test MCP endpoint with malformed JSON."""
        response = client.post("/mcp", data="invalid json")
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_mcp_endpoint_empty_body(self, client):
        """Test MCP endpoint with empty body."""
        response = client.post("/mcp")
        
        assert response.status_code == 422  # Unprocessable Entity

    def test_mcp_endpoint_missing_params(self, client):
        """Test MCP endpoint with missing params."""
        request = {
            "jsonrpc": "2.0",
            "id": 7,
            "method": "resources/read"
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Missing resource URI" in data["detail"]

    def test_mcp_endpoint_n8n_compatibility_tools(self, client):
        """Test that tools endpoint is compatible with n8n requirements."""
        request = {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        tools = result["tools"]
        
        # n8n requires specific tool structure
        for tool in tools:
            # Check required fields
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # Check inputSchema is valid JSON Schema
            input_schema = tool["inputSchema"]
            assert isinstance(input_schema, dict)
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            
            # Check for properties if they exist
            if "properties" in input_schema:
                assert isinstance(input_schema["properties"], dict)
                
                # Check each property has a type
                for prop_name, prop_schema in input_schema["properties"].items():
                    assert isinstance(prop_schema, dict)
                    assert "type" in prop_schema
                    assert prop_schema["type"] in ["string", "integer", "number", "boolean", "array", "object"]

    def test_mcp_endpoint_n8n_compatibility_resources(self, client):
        """Test that resources endpoint is compatible with n8n requirements."""
        request = {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "resources/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        resources = result["resources"]
        
        # n8n requires specific resource structure
        for resource in resources:
            # Check required fields
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
            
            # Check URI format
            assert isinstance(resource["uri"], str)
            assert "://" in resource["uri"]
            
            # Check MIME type format
            assert isinstance(resource["mimeType"], str)
            assert "/" in resource["mimeType"]

    def test_mcp_endpoint_error_handling_server_error(self, client):
        """Test MCP endpoint error handling for server errors."""
        # Mock the server to raise an exception
        with patch('server.http_server.mcp_server') as mock_server:
            mock_server.list_tools = AsyncMock(side_effect=Exception("Server error"))
            
            request = {
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/list",
                "params": {}
            }
            
            response = client.post("/mcp", json=request)
            
            assert response.status_code == 200
            data = response.json()
            
            # Check JSON-RPC 2.0 error format
            assert data["jsonrpc"] == "2.0"
            assert data["id"] == 10
            assert "error" in data
            
            error = data["error"]
            assert "code" in error
            assert "message" in error
            assert error["code"] == -32603  # Internal error

    def test_mcp_endpoint_content_type_header(self, client):
        """Test that MCP endpoint returns correct content type header."""
        request = {
            "jsonrpc": "2.0",
            "id": 11,
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_mcp_endpoint_cors_headers(self, client):
        """Test that MCP endpoint includes CORS headers."""
        request = {
            "jsonrpc": "2.0",
            "id": 12,
            "method": "initialize",
            "params": {}
        }
        
        # Simulate a cross-origin request by adding Origin header
        response = client.post("/mcp", json=request, headers={"Origin": "https://n8n.io"})
        
        assert response.status_code == 200
        # CORS headers should be present (handled by FastAPI middleware)
        assert "access-control-allow-origin" in response.headers

    def test_mcp_endpoint_large_request_handling(self, client):
        """Test MCP endpoint handles large requests properly."""
        # Create a large request with many parameters
        large_params = {
            "param1": "value1" * 1000,  # Large string
            "param2": list(range(1000)),  # Large list
            "param3": {"nested": "data" * 500}  # Large object
        }
        
        request = {
            "jsonrpc": "2.0",
            "id": 13,
            "method": "tools/list",
            "params": large_params
        }
        
        response = client.post("/mcp", json=request)
        
        # Should handle large requests gracefully
        assert response.status_code in [200, 400, 413]  # 413 = Payload Too Large

    def test_mcp_endpoint_concurrent_requests(self, client):
        """Test MCP endpoint handles concurrent requests."""
        import asyncio
        import concurrent.futures
        
        def make_request():
            request = {
                "jsonrpc": "2.0",
                "id": 14,
                "method": "initialize",
                "params": {}
            }
            return client.post("/mcp", json=request)
        
        # Make multiple concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [future.result() for future in futures]
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
            data = response.json()
            assert data["jsonrpc"] == "2.0"
            assert "result" in data

    def test_mcp_endpoint_input_schema_validation(self, client):
        """Test that input schemas are properly validated for n8n."""
        request = {
            "jsonrpc": "2.0",
            "id": 15,
            "method": "tools/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        tools = result["tools"]
        
        for tool in tools:
            input_schema = tool["inputSchema"]
            
            # Validate JSON Schema structure
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            
            # If properties exist, validate them
            if "properties" in input_schema:
                properties = input_schema["properties"]
                assert isinstance(properties, dict)
                
                for prop_name, prop_schema in properties.items():
                    assert isinstance(prop_name, str)
                    assert isinstance(prop_schema, dict)
                    assert "type" in prop_schema
                    
                    # Validate property types
                    prop_type = prop_schema["type"]
                    assert prop_type in ["string", "integer", "number", "boolean", "array", "object"]
                    
                    # If it's an array, check items
                    if prop_type == "array" and "items" in prop_schema:
                        assert isinstance(prop_schema["items"], dict)
                    
                    # If it's an object, check properties
                    if prop_type == "object" and "properties" in prop_schema:
                        assert isinstance(prop_schema["properties"], dict)

    def test_mcp_endpoint_method_not_found_error_format(self, client):
        """Test that method not found errors follow JSON-RPC 2.0 format."""
        request = {
            "jsonrpc": "2.0",
            "id": 16,
            "method": "nonexistent/method",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check JSON-RPC 2.0 error format
        assert data["jsonrpc"] == "2.0"
        assert data["id"] == 16
        assert "error" in data
        
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert error["code"] == -32601  # Method not found
        assert "Method 'nonexistent/method' not found" in error["message"]

    def test_mcp_endpoint_invalid_json_rpc_version(self, client):
        """Test MCP endpoint with invalid JSON-RPC version."""
        request = {
            "jsonrpc": "1.0",  # Invalid version
            "id": 17,
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        # Should still work as we don't validate JSON-RPC version
        assert response.status_code == 200

    def test_mcp_endpoint_missing_json_rpc_version(self, client):
        """Test MCP endpoint with missing JSON-RPC version."""
        request = {
            "id": 18,
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        # Should still work as we don't validate JSON-RPC version
        assert response.status_code == 200

    def test_mcp_endpoint_null_id(self, client):
        """Test MCP endpoint with null ID."""
        request = {
            "jsonrpc": "2.0",
            "id": None,
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is None

    def test_mcp_endpoint_string_id(self, client):
        """Test MCP endpoint with string ID."""
        request = {
            "jsonrpc": "2.0",
            "id": "string_id",
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "string_id"


class TestMCPEndpointN8NCompatibility:
    """Specific tests for n8n compatibility requirements."""

    @pytest.fixture
    def client(self):
        """Create a test client for the FastAPI app."""
        return TestClient(app)

    def test_n8n_tool_schema_compatibility(self, client):
        """Test that tool schemas are compatible with n8n requirements."""
        request = {
            "jsonrpc": "2.0",
            "id": 20,
            "method": "tools/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        tools = data["result"]["tools"]
        
        for tool in tools:
            # n8n requires specific tool structure
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            
            # n8n requires inputSchema to be a valid JSON Schema object
            input_schema = tool["inputSchema"]
            assert isinstance(input_schema, dict)
            assert "type" in input_schema
            assert input_schema["type"] == "object"
            
            # n8n expects properties to be defined
            if "properties" in input_schema:
                properties = input_schema["properties"]
                assert isinstance(properties, dict)
                
                for prop_name, prop_schema in properties.items():
                    # n8n requires each property to have a type
                    assert "type" in prop_schema
                    prop_type = prop_schema["type"]
                    
                    # n8n supports these types
                    assert prop_type in ["string", "integer", "number", "boolean", "array", "object"]
                    
                    # n8n requires description for better UX
                    if "description" not in prop_schema:
                        # This is optional but recommended
                        pass

    def test_n8n_resource_schema_compatibility(self, client):
        """Test that resource schemas are compatible with n8n requirements."""
        request = {
            "jsonrpc": "2.0",
            "id": 21,
            "method": "resources/list",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        resources = data["result"]["resources"]
        
        for resource in resources:
            # n8n requires specific resource structure
            assert "uri" in resource
            assert "name" in resource
            assert "description" in resource
            assert "mimeType" in resource
            
            # n8n expects URI to be a valid URI format
            uri = resource["uri"]
            assert isinstance(uri, str)
            assert "://" in uri
            
            # n8n expects MIME type to be valid
            mime_type = resource["mimeType"]
            assert isinstance(mime_type, str)
            assert "/" in mime_type

    def test_n8n_error_handling_compatibility(self, client):
        """Test that error handling is compatible with n8n requirements."""
        # Test method not found
        request = {
            "jsonrpc": "2.0",
            "id": 22,
            "method": "invalid/method",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        data = response.json()
        
        # n8n expects JSON-RPC 2.0 error format
        assert "error" in data
        error = data["error"]
        assert "code" in error
        assert "message" in error
        
        # n8n expects specific error codes
        assert error["code"] == -32601  # Method not found

    def test_n8n_content_type_compatibility(self, client):
        """Test that content type headers are compatible with n8n."""
        request = {
            "jsonrpc": "2.0",
            "id": 23,
            "method": "initialize",
            "params": {}
        }
        
        response = client.post("/mcp", json=request)
        
        assert response.status_code == 200
        
        # n8n expects JSON content type
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type

    def test_n8n_cors_compatibility(self, client):
        """Test that CORS headers are compatible with n8n."""
        request = {
            "jsonrpc": "2.0",
            "id": 24,
            "method": "initialize",
            "params": {}
        }
        
        # Simulate a cross-origin request by adding Origin header
        response = client.post("/mcp", json=request, headers={"Origin": "https://n8n.io"})
        
        assert response.status_code == 200
        
        # n8n expects CORS headers for cross-origin requests
        # These are handled by FastAPI CORS middleware
        cors_headers = [
            "access-control-allow-origin",
            "access-control-allow-methods",
            "access-control-allow-headers"
        ]
        
        # At least one CORS header should be present
        has_cors_header = any(header in response.headers for header in cors_headers)
        assert has_cors_header or "*" in response.headers.get("access-control-allow-origin", "")

    def test_n8n_request_size_compatibility(self, client):
        """Test that the endpoint handles request sizes compatible with n8n."""
        # n8n may send large requests, so we test with a reasonable size
        large_params = {
            "large_string": "x" * 10000,  # 10KB string
            "large_array": list(range(1000)),  # Large array
            "nested_object": {
                "level1": {
                    "level2": {
                        "level3": "deep_value"
                    }
                }
            }
        }
        
        request = {
            "jsonrpc": "2.0",
            "id": 25,
            "method": "tools/list",
            "params": large_params
        }
        
        response = client.post("/mcp", json=request)
        
        # Should handle large requests gracefully
        assert response.status_code in [200, 400, 413]

    def test_n8n_concurrent_request_compatibility(self, client):
        """Test that the endpoint handles concurrent requests from n8n."""
        import threading
        import time
        
        results = []
        errors = []
        
        def make_request(request_id):
            try:
                request = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "initialize",
                    "params": {}
                }
                response = client.post("/mcp", json=request)
                results.append((request_id, response.status_code))
            except Exception as e:
                errors.append((request_id, str(e)))
        
        # Create multiple threads to simulate concurrent n8n requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 10
        
        # All requests should succeed
        for request_id, status_code in results:
            assert status_code == 200, f"Request {request_id} failed with status {status_code}" 