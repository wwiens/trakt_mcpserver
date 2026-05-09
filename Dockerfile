# mcp-proxy + Trakt MCP server (SSE -> stdio)
FROM ghcr.io/sparfenyuk/mcp-proxy:latest

ARG VERSION=dev
ARG REPO_URL=https://github.com/wwiens/trakt_mcpserver
LABEL org.opencontainers.image.version=${VERSION}
LABEL org.opencontainers.image.source=${REPO_URL}
LABEL org.opencontainers.image.title="trakt-mcp-server"
LABEL org.opencontainers.image.description="MCP server for Trakt.tv"

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

# Layer 1 — deps from pyproject.toml only (cache key is pyproject.toml)
COPY pyproject.toml ./
RUN python3 -c "import tomllib; \
print('\n'.join(tomllib.load(open('pyproject.toml','rb'))['project']['dependencies']))" \
      > /tmp/requirements.txt \
    && pip3 install --no-cache-dir --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# Layer 2 — source + project metadata install (deps already satisfied)
COPY . .
RUN pip3 install --no-cache-dir --break-system-packages --no-deps .

# Back to root workdir
WORKDIR /app

# Create data directory for auth token persistence
RUN mkdir -p /data && chown -R appuser:appuser /data

# Change ownership of application files to non-root user
RUN chown -R appuser:appuser /app

# Environment variables (pass at runtime via -e or --env-file)
ENV TRAKT_CLIENT_ID=""
ENV TRAKT_CLIENT_SECRET=""
ENV TRAKT_AUTH_TOKEN_PATH=/data/auth_token.json

# Expose SSE port (will be overridden by runtime environment)
EXPOSE 8080

# Declare volume for auth token persistence across container restarts
VOLUME /data

# Switch to non-root user
USER appuser

# Run as: SSE proxy on 0.0.0.0:8080 -> spawn local stdio server
# --port fixes the listening port (default would be random if omitted)
# --pass-environment forwards TRAKT_* vars to the child process
# `--` separates proxy args from child args
ENTRYPOINT ["mcp-proxy"]
CMD ["--host", "0.0.0.0", "--port", "8080", "--pass-environment", "--", "python3", "/app/trakt_mcpserver/server.py"]
