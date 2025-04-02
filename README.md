# MCP Trakt

A Model Context Protocol (MCP) server that provides an interface between an LLM and the Trakt API.

## Features

- Exposes Trakt API data through MCP resources
- Provides tools for fetching shows information
- Currently supports:
  - Trending shows
  - Popular shows

## Setup

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and add your Trakt API credentials:
   ```
   cp .env.example .env
   ```
4. Run the server:
   ```
   python server.py
   ```

## Development

To test the server with the MCP Inspector:

```
mcp dev server.py
```

Or to install it directly in Claude Desktop:

```
mcp install server.py
``` 