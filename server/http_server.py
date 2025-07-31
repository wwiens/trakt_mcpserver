"""HTTP server for the Trakt MCP server."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .main import create_server


def ensure_valid_input_schema(tool) -> dict:
    """Ensure that a tool's input schema is valid for n8n compatibility.
    
    Args:
        tool: The tool object to process
        
    Returns:
        A valid input schema dictionary with type: 'object'
    """
    # Get the input schema and ensure it's properly formatted
    input_schema = getattr(tool, 'input_schema', {})
    
    # Always ensure we have a proper JSON schema structure for n8n compatibility
    if isinstance(input_schema, dict):
        # If input_schema is already a dict, ensure it has the correct type
        if 'type' not in input_schema:
            input_schema['type'] = 'object'
        elif input_schema['type'] != 'object':
            # Convert to object type for n8n compatibility
            input_schema = {
                'type': 'object',
                'properties': input_schema
            }
    else:
        # If input_schema is not a dict, create a default object schema
        input_schema = {'type': 'object'}
    
    # For tools with parameters, we need to ensure the schema has properties
    # Get the tool function to inspect its parameters
    tool_func = getattr(tool, 'function', None)
    if tool_func and hasattr(tool_func, '__annotations__'):
        # Extract parameter information from function annotations
        annotations = tool_func.__annotations__
        if annotations:
            # Create properties based on function parameters
            properties = {}
            for param_name, param_type in annotations.items():
                if param_name != 'return':
                    # Map Python types to JSON schema types
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
            
            # Update the input schema with properties
            if properties:
                input_schema = {
                    'type': 'object',
                    'properties': properties,
                    'required': list(properties.keys())
                }
    
    # Final validation: ensure input_schema is always a dict with type: object
    if not isinstance(input_schema, dict):
        input_schema = {'type': 'object'}
    elif 'type' not in input_schema or input_schema['type'] != 'object':
        input_schema = {'type': 'object'}
    
    return input_schema


def get_version() -> str:
    """Read version from VERSION.txt file."""
    try:
        # Get the project root directory (parent of server directory)
        project_root = Path(__file__).parent.parent
        version_file = project_root / "VERSION.txt"
        
        if version_file.exists():
            with open(version_file, 'r') as f:
                version = f.read().strip()
                return version
        else:
            logger.warning("VERSION.txt not found, using default version")
            return "1.0.0"
    except Exception as e:
        logger.error(f"Error reading version file: {e}")
        return "1.0.0"


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("trakt_mcp_http")

# Configure uvicorn logging to reduce noise
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.setLevel(logging.WARNING)

# Configure uvicorn access logger
uvicorn_access_logger = logging.getLogger("uvicorn.access")
uvicorn_access_logger.setLevel(logging.WARNING)

# Configure uvicorn error logger
uvicorn_error_logger = logging.getLogger("uvicorn.error")
uvicorn_error_logger.setLevel(logging.WARNING)

# Get version
VERSION = get_version()

# Create FastAPI app
app = FastAPI(
    title="Trakt MCP Server",
    description="HTTP interface for the Trakt MCP server",
    version=VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware to handle malformed requests
@app.middleware("http")
async def handle_malformed_requests(request: Request, call_next):
    """Handle malformed HTTP requests gracefully."""
    try:
        # Check if the request has a valid method
        if not request.method or request.method not in ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]:
            logger.debug(f"Invalid HTTP method received: {getattr(request, 'method', 'unknown')}")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid HTTP method"}
            )
        
        # Check if the request has a valid path
        if not request.url.path:
            logger.debug("Invalid HTTP request - missing path")
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid request path"}
            )
        
        response = await call_next(request)
        return response
        
    except Exception as e:
        # Log malformed requests at debug level instead of warning
        logger.debug(f"Malformed HTTP request handled: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid HTTP request"}
        )

# Create MCP server instance
mcp_server = create_server()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "trakt-mcp-server"}


@app.get("/")
async def root():
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
async def list_tools():
    """List available MCP tools."""
    try:
        tools = await mcp_server.list_tools()
        # Convert Tool objects to dictionaries
        tools_list = []
        for tool in tools:
            try:
                # Ensure the input schema is valid for n8n compatibility
                input_schema = ensure_valid_input_schema(tool)
                
                tools_list.append({
                    "name": getattr(tool, 'name', 'Unknown'),
                    "description": getattr(tool, 'description', 'No description'),
                    "inputSchema": input_schema
                })
            except Exception as tool_error:
                logger.error(f"Error processing tool: {tool_error}")
                # Add a placeholder for problematic tools
                tools_list.append({
                    "name": "error_tool",
                    "description": f"Error processing tool: {str(tool_error)}",
                    "inputSchema": {"type": "object"}
                })
        return {"tools": tools_list}
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/resources")
async def list_resources():
    """List available MCP resources."""
    try:
        resources = await mcp_server.list_resources()
        # Convert Resource objects to dictionaries
        resources_list = []
        for resource in resources:
            try:
                resources_list.append({
                    "uri": getattr(resource, 'uri', 'unknown://'),
                    "name": getattr(resource, 'name', 'Unknown'),
                    "description": getattr(resource, 'description', 'No description'),
                    "mimeType": getattr(resource, 'mime_type', 'text/plain')
                })
            except Exception as resource_error:
                logger.error(f"Error processing resource: {resource_error}")
                # Add a placeholder for problematic resources
                resources_list.append({
                    "uri": "error://resource",
                    "name": "error_resource",
                    "description": f"Error processing resource: {str(resource_error)}",
                    "mimeType": "text/plain"
                })
        return {"resources": resources_list}
    except Exception as e:
        logger.error(f"Error listing resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Main MCP endpoint that handles all MCP protocol messages."""
    try:
        # Get the request body
        body = await request.json()
        
        # Extract the method and parameters
        method = body.get("method")
        params = body.get("params", {})
        id = body.get("id")
        
        if not method:
            raise HTTPException(status_code=400, detail="Missing 'method' in request")
        
        # Handle different MCP methods
        if method == "initialize":
            # Return server capabilities
            response = {
                "jsonrpc": "2.0",
                "id": id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {},
                        "prompts": {}
                    },
                    "serverInfo": {
                        "name": "trakt-mcp-server",
                        "version": VERSION
                    }
                }
            }
        elif method == "tools/list":
            # List available tools
            try:
                tools = await mcp_server.list_tools()
                # Convert Tool objects to dictionaries
                tools_list = []
                for tool in tools:
                    try:
                        # Ensure the input schema is valid for n8n compatibility
                        input_schema = ensure_valid_input_schema(tool)
                        
                        tools_list.append({
                            "name": getattr(tool, 'name', 'Unknown'),
                            "description": getattr(tool, 'description', 'No description'),
                            "inputSchema": input_schema
                        })
                    except Exception as tool_error:
                        logger.error(f"Error processing tool: {tool_error}")
                        # Add a placeholder for problematic tools
                        tools_list.append({
                            "name": "error_tool",
                            "description": f"Error processing tool: {str(tool_error)}",
                            "inputSchema": {"type": "object"}
                        })
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {"tools": tools_list}
                }
            except Exception as e:
                logger.error(f"Error listing tools: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error listing tools: {str(e)}"
                    }
                }
        elif method == "tools/call":
            # Call a specific tool
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if not tool_name:
                raise HTTPException(status_code=400, detail="Missing tool name")
            
            try:
                result = await mcp_server.call_tool(tool_name, arguments)
                
                # Handle TextContent objects by extracting the text content
                if hasattr(result, 'text'):
                    result_content = result.text
                    logger.debug(f"Extracted text content from TextContent object for tool {tool_name}")
                elif hasattr(result, 'content'):
                    result_content = result.content
                    logger.debug(f"Extracted content from object for tool {tool_name}")
                else:
                    result_content = str(result)
                    logger.debug(f"Converted result to string for tool {tool_name}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {"content": result_content}
                }
            except Exception as e:
                logger.error(f"Error calling tool {tool_name}: {e}")
                logger.error(f"Result type: {type(result) if 'result' in locals() else 'Not available'}")
                logger.error(f"Result attributes: {dir(result) if 'result' in locals() and hasattr(result, '__dict__') else 'Not available'}")
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error calling tool: {str(e)}"
                    }
                }
        elif method == "resources/list":
            # List available resources
            try:
                resources = await mcp_server.list_resources()
                # Convert Resource objects to dictionaries
                resources_list = []
                for resource in resources:
                    try:
                        resources_list.append({
                            "uri": getattr(resource, 'uri', 'unknown://'),
                            "name": getattr(resource, 'name', 'Unknown'),
                            "description": getattr(resource, 'description', 'No description'),
                            "mimeType": getattr(resource, 'mime_type', 'text/plain')
                        })
                    except Exception as resource_error:
                        logger.error(f"Error processing resource: {resource_error}")
                        # Add a placeholder for problematic resources
                        resources_list.append({
                            "uri": "error://resource",
                            "name": "error_resource",
                            "description": f"Error processing resource: {str(resource_error)}",
                            "mimeType": "text/plain"
                        })
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {"resources": resources_list}
                }
            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error listing resources: {str(e)}"
                    }
                }
        elif method == "resources/read":
            # Read a specific resource
            uri = params.get("uri")
            
            if not uri:
                raise HTTPException(status_code=400, detail="Missing resource URI")
            
            try:
                content = await mcp_server.read_resource(uri)
                
                # Handle TextContent objects by extracting the text content
                if hasattr(content, 'text'):
                    content_text = content.text
                    logger.debug(f"Extracted text content from TextContent object for resource {uri}")
                elif hasattr(content, 'content'):
                    content_text = content.content
                    logger.debug(f"Extracted content from object for resource {uri}")
                else:
                    content_text = str(content)
                    logger.debug(f"Converted content to string for resource {uri}")
                
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "result": {
                        "contents": [{
                            "uri": uri,
                            "mimeType": "text/markdown",  # Default MIME type
                            "text": content_text
                        }]
                    }
                }
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                logger.error(f"Content type: {type(content) if 'content' in locals() else 'Not available'}")
                logger.error(f"Content attributes: {dir(content) if 'content' in locals() and hasattr(content, '__dict__') else 'Not available'}")
                response = {
                    "jsonrpc": "2.0",
                    "id": id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error reading resource: {str(e)}"
                    }
                }
        else:
            # Unknown method
            response = {
                "jsonrpc": "2.0",
                "id": id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found"
                }
            }
        
        return JSONResponse(content=response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in MCP endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the HTTP server."""
    logger.info(f"Starting Trakt MCP HTTP server on {host}:{port}")
    
    # Get configuration from environment variables
    log_level = os.getenv("UVICORN_LOG_LEVEL", "warning")
    access_log = os.getenv("UVICORN_ACCESS_LOG", "false").lower() == "true"
    
    # Configure uvicorn to reduce invalid HTTP request warnings
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level=log_level,    # Use environment variable
        access_log=access_log,   # Use environment variable
        server_header=False,     # Disable server header
        date_header=False        # Disable date header
    )


if __name__ == "__main__":
    run_server() 