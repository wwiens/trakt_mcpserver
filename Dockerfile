# mcp-proxy + Trakt MCP server (SSE -> stdio)
FROM ghcr.io/sparfenyuk/mcp-proxy:latest

# Install Python and tools (base image is Alpine)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    ca-certificates

# Workdir
WORKDIR /app

# Copy Trakt MCP server sources
COPY server requirements.txt ./trakt-server/

# Install Python dependencies
WORKDIR /app/trakt-server
RUN pip3 install --no-cache-dir -r requirements.txt

# Back to root workdir
WORKDIR /app

# Trakt credentials (override at runtime)
ENV TRAKT_CLIENT_ID=""
ENV TRAKT_CLIENT_SECRET=""

# Expose SSE port
EXPOSE 8080

# Run as: SSE proxy on 0.0.0.0:8080 -> spawn local stdio server
# --port fixes the listening port (default would be random if omitted)
# --pass-environment forwards TRAKT_* vars to the child process
# `--` separates proxy args from child args
ENTRYPOINT ["mcp-proxy"]
CMD ["--host", "0.0.0.0", "--port", "8080", "--pass-environment", "--", "python3", "/app/trakt-server/server.py"]
