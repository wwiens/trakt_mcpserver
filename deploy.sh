#!/bin/bash

# Trakt MCP Server Deployment Script
# This script helps deploy the Trakt MCP server using Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="trakt-mcp-server"
CONTAINER_NAME="trakt-mcp-server"
PORT=${PORT:-8000}
HOST=${HOST:-"0.0.0.0"}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build the Docker image
build_image() {
    print_status "Building Docker image..."
    docker build -t $IMAGE_NAME .
    print_success "Docker image built successfully"
}

# Function to stop and remove existing container
cleanup_container() {
    if docker ps -a --format "table {{.Names}}" | grep -q "^$CONTAINER_NAME$"; then
        print_status "Stopping existing container..."
        docker stop $CONTAINER_NAME > /dev/null 2>&1 || true
        print_status "Removing existing container..."
        docker rm $CONTAINER_NAME > /dev/null 2>&1 || true
        print_success "Container cleanup completed"
    fi
}

# Function to run the container
run_container() {
    print_status "Starting container..."
    # Source .env if it exists
    if [ -f .env ]; then set -a; . .env; set +a; fi
    docker run -d \
        --name $CONTAINER_NAME \
        -p $PORT:8000 \
        -e HOST=$HOST \
        -e PORT=8000 \
        -e LOG_LEVEL=INFO \
        -e UVICORN_LOG_LEVEL=warning \
        -e UVICORN_ACCESS_LOG=false \
        --restart unless-stopped \
        $IMAGE_NAME
    
    print_success "Container started successfully"
}

# Function to wait for server to be ready
wait_for_server() {
    print_status "Waiting for server to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            print_success "Server is ready!"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts - Server not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "Server failed to start within expected time"
    return 1
}

# Function to show server information
show_server_info() {
    echo
    print_success "Trakt MCP Server is now running!"
    echo
    echo "Server Information:"
    echo "  - Container Name: $CONTAINER_NAME"
    echo "  - Host: $HOST"
    echo "  - Port: $PORT"
    echo "  - Health Check: http://localhost:$PORT/health"
    echo "  - Server Info: http://localhost:$PORT/"
    echo "  - Tools List: http://localhost:$PORT/tools"
    echo "  - Resources List: http://localhost:$PORT/resources"
    echo "  - MCP Endpoint: http://localhost:$PORT/mcp"
    echo
    echo "For Claude Desktop, use: http://localhost:$PORT/mcp"
    echo
    echo "Useful commands:"
    echo "  - View logs: docker logs $CONTAINER_NAME"
    echo "  - Follow logs: docker logs -f $CONTAINER_NAME"
    echo "  - Stop server: docker stop $CONTAINER_NAME"
    echo "  - Restart server: docker restart $CONTAINER_NAME"
    echo "  - Remove server: docker rm -f $CONTAINER_NAME"
    echo
}

# Function to test the server
test_server() {
    print_status "Testing server endpoints..."
    if python tests/http_server/test_http_server.py http://localhost:$PORT; then
        print_success "Server test completed successfully"
    else
        print_warning "Server test failed - check logs with 'docker logs $CONTAINER_NAME'"
    fi
}

# Main deployment function
deploy() {
    print_status "Starting Trakt MCP Server deployment..."
    
    check_docker
    cleanup_container
    build_image
    run_container
    wait_for_server
    show_server_info
    test_server
}

# Function to show help
show_help() {
    echo "Trakt MCP Server Deployment Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  -p, --port     Port to expose (default: 8000)"
    echo "  -H, --host     Host to bind to (default: 0.0.0.0)"
    echo "  -t, --test     Only test the server (assumes it's already running)"
    echo "  -c, --cleanup  Only cleanup existing container"
    echo
    echo "Environment variables:"
    echo "  PORT           Port to expose (default: 8000)"
    echo "  HOST           Host to bind to (default: 0.0.0.0)"
    echo
    echo "Examples:"
    echo "  $0                    # Deploy with default settings"
    echo "  $0 -p 9000           # Deploy on port 9000"
    echo "  $0 -t                # Test existing server"
    echo "  $0 -c                # Cleanup existing container"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -H|--host)
            HOST="$2"
            shift 2
            ;;
        -t|--test)
            test_server
            exit 0
            ;;
        -c|--cleanup)
            cleanup_container
            print_success "Cleanup completed"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Run deployment
deploy 