"""Client modules for the Trakt MCP server.

This module provides domain-focused HTTP clients for Trakt API interactions:

- client.auth: Authentication client (AuthClient)
- client.checkin: Check-in client (CheckinClient)
- client.comments: Comments client (CommentsClient)
- client.movies: Movies client (MoviesClient)
- client.search: Search client (SearchClient)
- client.shows: Shows client (ShowsClient)
- client.user: User data client (UserClient)
- client.base: Base client functionality (BaseClient)

Use direct imports for better clarity:
    from client.auth import AuthClient
    from client.shows import ShowsClient
    from client.movies import MoviesClient
    # etc.
"""
