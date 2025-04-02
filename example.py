#!/usr/bin/env python3
"""Example script to test the Trakt client directly."""

import asyncio
import json
from trakt_client import TraktClient
from models import FormatHelper


async def main():
    """Run a simple demonstration of the Trakt client."""
    client = TraktClient()
    
    print("Fetching trending shows...")
    trending_shows = await client.get_trending_shows(limit=5)
    
    print("\nRaw JSON response:")
    print(json.dumps(trending_shows, indent=2))
    
    print("\nFormatted trending shows:")
    print(FormatHelper.format_trending_shows(trending_shows))
    
    print("\nFetching popular shows...")
    popular_shows = await client.get_popular_shows(limit=5)
    
    print("\nRaw JSON response:")
    print(json.dumps(popular_shows, indent=2))
    
    print("\nFormatted popular shows:")
    print(FormatHelper.format_popular_shows(popular_shows))


if __name__ == "__main__":
    asyncio.run(main()) 