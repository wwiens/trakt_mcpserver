# MCP Trakt

A Model Context Protocol (MCP) server that provides an interface between an LLM and the Trakt API.

## Features

- Exposes Trakt API data through MCP resources
- Provides tools for fetching movies and shows information

### Available Resources

#### Show Resources
- `trakt://shows/trending` - Most watched shows over the last 24 hours
- `trakt://shows/popular` - Most popular shows based on ratings
- `trakt://shows/favorited` - Most favorited shows 
- `trakt://shows/played` - Most played shows
- `trakt://shows/watched` - Most watched shows by unique users

#### Movie Resources
- `trakt://movies/trending` - Most watched movies over the last 24 hours
- `trakt://movies/popular` - Most popular movies based on ratings
- `trakt://movies/favorited` - Most favorited movies
- `trakt://movies/played` - Most played movies
- `trakt://movies/watched` - Most watched movies by unique users

### Available Tools

#### Show Tools
- `fetch_trending_shows` - Get trending shows with optional limit parameter
- `fetch_popular_shows` - Get popular shows with optional limit parameter
- `fetch_favorited_shows` - Get favorited shows with optional limit and period parameters
- `fetch_played_shows` - Get most played shows with optional limit and period parameters
- `fetch_watched_shows` - Get most watched shows with optional limit and period parameters

#### Movie Tools
- `fetch_trending_movies` - Get trending movies with optional limit parameter
- `fetch_popular_movies` - Get popular movies with optional limit parameter
- `fetch_favorited_movies` - Get favorited movies with optional limit and period parameters
- `fetch_played_movies` - Get most played movies with optional limit and period parameters
- `fetch_watched_movies` - Get most watched movies with optional limit and period parameters

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