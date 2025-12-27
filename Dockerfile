# mcp-proxy + Trakt MCP server (SSE -> stdio)
FROM ghcr.io/sparfenyuk/mcp-proxy:latest

# Install Python and tools (base image is Alpine)
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    ca-certificates

# Create a non-root user and group
RUN addgroup -g 1000 -S appuser && \
    adduser -u 1000 -S appuser -G appuser

# Workdir
WORKDIR /app/trakt_mcpserver

# Copy project (everything except what's in .dockerignore)
COPY . .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Back to root workdir
WORKDIR /app

# Change ownership of application files to non-root user
RUN chown -R appuser:appuser /app

# Environment variables (pass at runtime via -e or --env-file)
ENV TRAKT_CLIENT_ID=""
ENV TRAKT_CLIENT_SECRET=""

# Expose SSE port (will be overridden by runtime environment)
EXPOSE 8080

# Switch to non-root user
USER appuser

# Run as: SSE proxy on 0.0.0.0:8080 -> spawn local stdio server
# --port fixes the listening port (default would be random if omitted)
# --pass-environment forwards TRAKT_* vars to the child process
# `--` separates proxy args from child args
ENTRYPOINT ["mcp-proxy"]
CMD ["--host", "0.0.0.0", "--port", "8080", "--pass-environment", "--", "python3", "/app/trakt_mcpserver/server.py"]
