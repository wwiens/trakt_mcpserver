# MCP Endpoint Tests

This directory contains comprehensive tests for the `/mcp` endpoint to ensure compatibility with n8n and other MCP clients.

## Overview

The MCP (Model Context Protocol) endpoint tests verify that the Trakt MCP server properly implements the MCP specification and is compatible with n8n workflow automation platform.

## Test Files

### 1. `test_mcp_endpoint.py`
Comprehensive pytest-based tests for the MCP endpoint:

- **Protocol Compliance**: JSON-RPC 2.0 compliance
- **Method Support**: All MCP methods (initialize, tools/list, resources/list, resources/read)
- **Error Handling**: Proper error codes and messages
- **n8n Compatibility**: Specific tests for n8n integration requirements
- **Performance**: Large request handling and concurrent requests

### 2. `test_mcp_runner.py`
Standalone test runner for MCP endpoint tests:

```bash
# Run all MCP tests
python tests/http_server/test_mcp_runner.py

# Run only n8n compatibility tests
python tests/http_server/test_mcp_runner.py --n8n-only

# Show help
python tests/http_server/test_mcp_runner.py --help
```

### 3. `N8N_COMPATIBILITY.md`
Detailed documentation explaining n8n compatibility requirements and implementation details.

## Quick Test

For a quick test without installing pytest, use the simple test script:

```bash
# Test against local server
python test_mcp_simple.py

# Test against specific server
python test_mcp_simple.py http://your-server:8000
```

## Test Categories

### 1. Basic MCP Protocol Tests
- JSON-RPC 2.0 compliance
- Request/response format validation
- Error handling with proper codes
- ID handling (string, number, null)

### 2. Method Support Tests
- `initialize` - Server information
- `tools/list` - Available tools
- `resources/list` - Available resources
- `resources/read` - Resource content

### 3. Error Handling Tests
- Missing method
- Invalid method
- Malformed JSON
- Missing parameters
- Server errors

### 4. n8n Compatibility Tests
- Tool schema validation
- Resource schema validation
- HTTP headers (Content-Type, CORS)
- Request size handling
- Concurrent request handling

## Running Tests

### Prerequisites
```bash
# Install development dependencies
pip install -r requirements-dev.txt
```

### Using pytest
```bash
# All MCP tests
pytest tests/http_server/test_mcp_endpoint.py -v

# Only n8n compatibility tests
pytest tests/http_server/test_mcp_endpoint.py::TestMCPEndpointN8NCompatibility -v

# Specific test
pytest tests/http_server/test_mcp_endpoint.py::TestMCPEndpoint::test_mcp_endpoint_initialize_success -v
```

### Using the test runner
```bash
# Run all tests
python tests/http_server/test_mcp_runner.py

# Run only n8n tests
python tests/http_server/test_mcp_runner.py --n8n-only
```

### Using the simple test script
```bash
# Test local server
python test_mcp_simple.py

# Test remote server
python test_mcp_simple.py http://remote-server:8000
```

## Test Results

### Success Criteria
- All JSON-RPC 2.0 requests return proper responses
- Error handling follows JSON-RPC 2.0 specification
- Tool schemas are valid JSON Schema
- Resource schemas include all required fields
- HTTP headers are properly set
- CORS is configured for cross-origin requests

### n8n Compatibility
- Tools have valid `inputSchema` with `type: "object"`
- Resources have valid URI and MIME type formats
- Error codes match JSON-RPC 2.0 specification
- Content-Type is `application/json`
- CORS headers allow n8n integration

## Troubleshooting

### Common Issues

1. **Server not running**
   ```bash
   # Start the server first
   python server/http_server.py
   ```

2. **Dependencies missing**
   ```bash
   # Install required packages
   pip install -r requirements-dev.txt
   ```

3. **CORS errors**
   - Check `ALLOWED_ORIGINS` environment variable
   - Ensure CORS middleware is enabled

4. **Schema validation errors**
   - Verify all tools have valid `inputSchema`
   - Check property types are supported

### Debug Mode

Enable debug logging for the server:

```bash
export UVICORN_LOG_LEVEL=debug
python server/http_server.py
```

## Integration with n8n

### HTTP Request Node Configuration

In n8n, configure the HTTP Request node:

- **Method**: POST
- **URL**: `http://your-server:8000/mcp`
- **Headers**: `Content-Type: application/json`
- **Body**: JSON-RPC 2.0 request

### Example Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}
```

### Example Response
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "get_trending_shows",
        "description": "Get trending shows from Trakt",
        "inputSchema": {
          "type": "object",
          "properties": {
            "limit": {
              "type": "integer",
              "description": "Number of shows to return"
            }
          }
        }
      }
    ]
  }
}
```

## Contributing

When adding new features to the MCP endpoint:

1. **Add tests** for new functionality
2. **Maintain n8n compatibility**
3. **Follow JSON-RPC 2.0 specification**
4. **Update documentation**
5. **Run the full test suite**

### Test Guidelines

- Test both success and error scenarios
- Verify JSON-RPC 2.0 compliance
- Check n8n compatibility requirements
- Test with large requests and concurrent access
- Validate schema formats

## Future Enhancements

1. **WebSocket Support**
   - Real-time communication tests
   - Event streaming validation

2. **Authentication Tests**
   - API key validation
   - OAuth flow testing

3. **Performance Tests**
   - Load testing
   - Memory usage monitoring

4. **Integration Tests**
   - End-to-end workflow testing
   - Real n8n workflow validation 