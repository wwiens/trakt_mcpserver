"""Process-wide cache of BaseClient instances for connection reuse.

Each cached instance keeps its underlying ``httpx.AsyncClient`` alive across
requests, so tools share TCP/TLS connections instead of re-handshaking on
every call. Direct ``SomeClient()`` instantiation is unaffected and still
opens/closes a fresh HTTP client per request (preserves test behavior).
"""

from __future__ import annotations

import threading
from typing import TypeVar, cast

from .base import BaseClient

T = TypeVar("T", bound=BaseClient)

_CACHE: dict[type[BaseClient], BaseClient] = {}
_LOCK = threading.Lock()


def get_client(cls: type[T]) -> T:
    """Return a cached singleton of the given client class.

    The returned instance persists its ``httpx.AsyncClient`` for the lifetime
    of the process, so subsequent requests reuse the connection pool.
    """
    with _LOCK:
        cached = _CACHE.get(cls)
        if cached is None:
            cached = cls()
            cached.enable_pooling()
            _CACHE[cls] = cached
    return cast("T", cached)


async def shutdown_clients() -> None:
    """Close all pooled HTTP clients. Call on process shutdown."""
    with _LOCK:
        cached_clients = list(_CACHE.values())
        _CACHE.clear()
    for client in cached_clients:
        await client.aclose()
