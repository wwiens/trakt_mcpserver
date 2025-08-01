"""HTTP server for the Trakt MCP server."""

import json
import logging
import os
from pathlib import Path
from typing import Any
from collections.abc import Callable, Awaitable

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
import uvicorn

from .main import create_server

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trakt_mcp_http")

# Configure uvicorn logging to reduce noise
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.WARNING)
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.WARNING)
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.setLevel(logging.WARNING)

def ensure_valid_input_schema(tool: Any) -> dict[str, Any]:
    """Ensure that a tool's input schema is valid for n8n compatibility.
    
    Args:
        tool: The tool object to process
    Returns:
        A valid input schema dictionary with type: 'object'
    """
    input_schema = getattr(tool, 'input_schema', {})
    if isinstance(input_schema, dict):
        if 'type' not in input_schema:
            input_schema['type'] = 'object'
        elif input_schema['type'] != 'object':
            input_schema = {
                'type': 'object',
                'properties': input_schema
            }
    else:
        input_schema = {'type': 'object'}
    tool_func = getattr(tool, 'function', None)
    if tool_func and hasattr(tool_func, '__annotations__'):
        annotations = tool_func.__annotations__
        if annotations:
            properties = {}
            for param_name, param_type in annotations.items():
                if param_name != 'return':
                    if param_type == str:
                        properties[param_name] = {'type': 'string'}
                    elif param_type == int:
                        properties[param_name] = {'type': 'integer'}
                    elif param_type == bool:
                        properties[param_name] = {'type': 'boolean'}
                    elif param_type == float:
                        properties[param_name] = {'type': 'number'}
                    else:
                        properties[param_name] = {'type': 'string'}
            if properties:
                input_schema = {
                    'type': 'object',
                    'properties': properties,
                    'required': list(properties.keys())
                }
    if not isinstance(input_schema, dict):
        input_schema = {'type': 'object'}
    elif 'type' not in input_schema or input_schema['type'] != 'object':
        input_schema = {'type': 'object'}
    return input_schema

def get_version() -> str:
    """Read version from VERSION.txt file."""
    try:
        project_root = Path(__file__).parent.parent
        version_file = project_root / "VERSION.txt"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                return version
        else:
            logger.warning("VERSION.txt not found, using default version")
            return "1.0.0"
    except Exception as e:
        logger.error(f"Error reading version file: {e}")
        return "1.0.0"

VERSION = get_version()

app = FastAPI(
    title="Trakt MCP Server",
    description="HTTP interface for the Trakt MCP server",
    version=VERSION
)

# CORS origins from environment variable
import ast
origins_env = os.getenv("ALLOWED_ORIGINS", "*")
if origins_env == "*":
    allowed_origins = ["*"]
else:
    try:
        allowed_origins = ast.literal_eval(origins_env) if origins_env.startswith("[") else [o.strip() for o in origins_env.split(",")]
    except Exception:
        allowed_origins = [origins_env]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def handle_malformed_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Handle malformed HTTP requests gracefully."""
    try:
        if not request.method or request.method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
            logger.debug(f"Invalid HTTP method received: {getattr(request, 'method', 'unknown')}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid HTTP method"}
            )
        if not request.url.path:
            logger.debug("Invalid HTTP request - missing path")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request path"}
            )
        response = await call_next(request)
        return response
    except Exception as e:
        logger.debug(f"Malformed HTTP request handled: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid HTTP request"}
        )

mcp_server = create_server()

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "trakt-mcp-server"}

@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint with server information."""
    return {
        "service": "Trakt MCP Server",
        "version": VERSION,
        "endpoints": {
            "health": "/health",
            "mcp": "/mcp",
            "tools": "/tools",
            "resources": "/resources"
        }
    }

@app.get("/tools")
async def list_tools() -> dict[str, Any]:
    """List available MCP tools."""
    try:
        tools = await mcp_server.list_tools()
        tools_list = []
        for tool in tools:
            try:
                input_schema = ensure_valid_input_schema(tool)
                tools_list.append({
                    "name": getattr(tool, 'name', 'Unknown'),
                    "description": getattr(tool, 'description', 'No description'),
                    "inputSchema": input_schema
                })
            except Exception as tool_error:
                logger.error(f"Error processing tool: {tool_error}")
                tools_list.append({
                    "name": "error_tool",
                    "description": f"Error processing tool: {str(tool_error)}",
                    "inputSchema": {"type": "object"}
                })
        return {"tools": tools_list}
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@app.get("/resources")
async def list_resources() -> dict[str, Any]:
    """List available MCP resources."""
    try:
        resources = await mcp_server.list_resources()
        resources_list = []
        for resource in resources:
            try:
                # Convert AnyUrl objects to strings for JSON serialization
                uri = getattr(resource, 'uri', 'unknown://')
                if hasattr(uri, '__str__'):
                    uri = str(uri)
                
                resources_list.append({
                    "uri": uri,
                    "name": getattr(resource, 'name', 'Unknown'),
                    "description": getattr(resource, 'description', 'No description'),
                    "mimeType": getattr(resource, 'mime_type', 'text/plain')
                })
            except Exception as resource_error:
                logger.error(f"Error processing resource: {resource_error}")
                resources_list.append({
                    "uri": "error://resource",
                    "name": "error_resource",
                    "description": f"Error processing resource: {str(resource_error)}",
                    "mimeType": "text/plain"
                })
        return {"resources": resources_list}
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@app.post("/mcp")
async def mcp_endpoint(request: Request) -> JSONResponse:
    """Main MCP endpoint that handles all MCP protocol messages."""
    try:
        body = await request.json()
        method = body.get("method")
        params = body.get("params", {})
        id = body.get("id")
        if not method:
            raise HTTPException(status_code=400, detail="Missing method in request body")
        if method == "initialize":
            return await _handle_initialize(id)
        elif method == "tools/list":
            return await _handle_tools_list(id)
        elif method == "resources/list":
            return await _handle_resources_list(id)
        elif method == "resources/read":
            return await _handle_resources_read(id, params)
        else:
            return JSONResponse(content={
                "jsonrpc": "2.0",
                "id": id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            })
    except HTTPException:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Malformed JSON in MCP endpoint: {e}")
        raise HTTPException(status_code=422, detail="Malformed JSON") from e
    except Exception as e:
        logger.error(f"Unexpected error in MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") from e

async def _handle_initialize(id: Any) -> JSONResponse:
    return JSONResponse(content={
        "jsonrpc": "2.0",
        "id": id,
        "result": {
            "serverInfo": {
                "service": "Trakt MCP Server",
                "version": VERSION
            }
        }
    })

async def _handle_tools_list(id: Any) -> JSONResponse:
    try:
        tools = await mcp_server.list_tools()
        tools_list = []
        for tool in tools:
            try:
                input_schema = ensure_valid_input_schema(tool)
                tools_list.append({
                    "name": getattr(tool, 'name', 'Unknown'),
                    "description": getattr(tool, 'description', 'No description'),
                    "inputSchema": input_schema
                })
            except Exception as tool_error:
                logger.error(f"Error processing tool: {tool_error}")
                tools_list.append({
                    "name": "error_tool",
                    "description": f"Error processing tool: {str(tool_error)}",
                    "inputSchema": {"type": "object"}
                })
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "result": {"tools": tools_list}
        })
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32603,
                "message": f"Internal error listing tools: {str(e)}"
            }
        })

async def _handle_resources_list(id: Any) -> JSONResponse:
    try:
        resources = await mcp_server.list_resources()
        resources_list = []
        for resource in resources:
            try:
                # Convert AnyUrl objects to strings for JSON serialization
                uri = getattr(resource, 'uri', 'unknown://')
                if hasattr(uri, '__str__'):
                    uri = str(uri)
                
                resources_list.append({
                    "uri": uri,
                    "name": getattr(resource, 'name', 'Unknown'),
                    "description": getattr(resource, 'description', 'No description'),
                    "mimeType": getattr(resource, 'mime_type', 'text/plain')
                })
            except Exception as resource_error:
                logger.error(f"Error processing resource: {resource_error}")
                resources_list.append({
                    "uri": "error://resource",
                    "name": "error_resource",
                    "description": f"Error processing resource: {str(resource_error)}",
                    "mimeType": "text/plain"
                })
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "result": {"resources": resources_list}
        })
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32603,
                "message": f"Internal error listing resources: {str(e)}"
            }
        })

async def _handle_resources_read(id: Any, params: dict[str, Any]) -> JSONResponse:
    uri = params.get("uri")
    if not uri:
        raise HTTPException(status_code=400, detail="Missing resource URI")
    try:
        content = await mcp_server.read_resource(uri)
        if hasattr(content, 'text'):
            content_text = content.text
            logger.debug(f"Extracted text content from TextContent object for resource {uri}")
        elif hasattr(content, 'content'):
            content_text = content.content
            logger.debug(f"Extracted content from object for resource {uri}")
        else:
            content_text = str(content)
            logger.debug(f"Converted content to string for resource {uri}")
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "result": {
                "contents": [{
                    "uri": uri,
                    "mimeType": "text/markdown",
                    "text": content_text
                }]
            }
        })
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {e}")
        return JSONResponse(content={
            "jsonrpc": "2.0",
            "id": id,
            "error": {
                "code": -32603,
                "message": f"Internal error reading resource: {str(e)}"
            }
        })

def run_server(host: str | None = None, port: int = 8000) -> None:
    """Run the HTTP server."""
    if host is None:
        host = os.getenv("HOST", "127.0.0.1")
    logger.info(f"Starting Trakt MCP HTTP server on {host}:{port}")
    log_level = os.getenv("UVICORN_LOG_LEVEL", "warning")
    access_log = os.getenv("UVICORN_ACCESS_LOG", "false").lower() == "true"
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level=log_level,
        access_log=access_log,
        server_header=False,
        date_header=False
    )

if __name__ == "__main__":
    run_server() 