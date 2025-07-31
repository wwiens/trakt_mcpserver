#!/usr/bin/env python3
"""Docker entrypoint script for the Trakt MCP server."""

import os
import sys
import logging
from server.http_server import run_server

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Main entry point for the Docker container."""
    try:
        # Get configuration from environment variables
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', '8000'))
        
        logger.info(f"Starting Trakt MCP HTTP server on {host}:{port}")
        logger.info("Server will be available at:")
        logger.info(f"  - Health check: http://{host}:{port}/health")
        logger.info(f"  - MCP endpoint: http://{host}:{port}/mcp")
        logger.info(f"  - Tools list: http://{host}:{port}/tools")
        logger.info(f"  - Resources list: http://{host}:{port}/resources")
        
        # Run the server
        run_server(host=host, port=port)
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 