#!/usr/bin/env python3
"""Test script to examine the favorited shows endpoint response structure."""

import asyncio
import json
from trakt_client import TraktClient


async def main():
    """Run a simple test of the favorited shows endpoint."""
    client = TraktClient()
    
    print("Fetching favorited shows...")
    favorited_shows = await client.get_favorited_shows(limit=5)
    
    print("\nRaw JSON response:")
    print(json.dumps(favorited_shows, indent=2))
    
    if favorited_shows and len(favorited_shows) > 0:
        print("\nFirst show structure:")
        first_show = favorited_shows[0]
        print(json.dumps(first_show, indent=2))
        
        print("\nAvailable keys in show object:")
        print(list(first_show.keys()))
        
        show_obj = first_show.get("show", {})
        print("\nShow sub-object:")
        print(json.dumps(show_obj, indent=2))
        
        print("\nUser count field (various names):")
        for field in ["user_count", "users", "count", "favorited", "favorites"]:
            print(f"{field}: {first_show.get(field)}")


if __name__ == "__main__":
    asyncio.run(main()) 