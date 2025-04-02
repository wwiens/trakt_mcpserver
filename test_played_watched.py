#!/usr/bin/env python3
"""Test script to examine the played and watched shows endpoint response structure."""

import asyncio
import json
from trakt_client import TraktClient


async def main():
    """Run a simple test of the played and watched shows endpoints."""
    client = TraktClient()
    
    # Test played shows
    print("Fetching played shows...")
    played_shows = await client.get_played_shows(limit=2)
    
    print("\nRaw JSON response for played shows:")
    print(json.dumps(played_shows, indent=2))
    
    if played_shows and len(played_shows) > 0:
        print("\nFirst played show structure:")
        first_show = played_shows[0]
        print(json.dumps(first_show, indent=2))
        
        print("\nAvailable keys in played show object:")
        print(list(first_show.keys()))
    
    # Test watched shows
    print("\n\nFetching watched shows...")
    watched_shows = await client.get_watched_shows(limit=2)
    
    print("\nRaw JSON response for watched shows:")
    print(json.dumps(watched_shows, indent=2))
    
    if watched_shows and len(watched_shows) > 0:
        print("\nFirst watched show structure:")
        first_show = watched_shows[0]
        print(json.dumps(first_show, indent=2))
        
        print("\nAvailable keys in watched show object:")
        print(list(first_show.keys()))


if __name__ == "__main__":
    asyncio.run(main()) 