"""Process-wide pool of ``BaseClient`` instances and their shared ``httpx.AsyncClient``.

All clients share a single ``httpx.AsyncClient`` for connection reuse across
Trakt API requests. Non-authenticated client *wrappers* are cached as
singletons per class. ``AuthClient`` wrappers are returned fresh per call so
each tool invocation re-reads ``auth_token.json`` from disk — auth state
(``self.auth_token``, ``self.headers``) lives on the wrapper, so caching it
would let login/refresh/clear go stale across tool calls. The shared httpx
client carries no auth state and is safe to share. Direct ``SomeClient()``
instantiation is unaffected and still opens/closes a fresh HTTP client per
request.
"""

from __future__ import annotations

import inspect
import threading
from typing import TypeGuard, TypeVar

import httpx

from .auth import AuthClient
from .base import BaseClient

T = TypeVar("T", bound=BaseClient)


def _is_instance_of(obj: object, cls: type[T]) -> TypeGuard[T]:
    """TypeGuard wrapper — ``isinstance(obj, cls)`` alone does not bind ``T``."""
    return isinstance(obj, cls)


_CACHE: dict[type[BaseClient], BaseClient] = {}
# Reentrant because ``get_client`` acquires the lock and then calls
# ``enable_pooling`` → ``get_or_create_shared_http`` which acquires it again.
_LOCK = threading.RLock()
_shared_http: httpx.AsyncClient | None = None


def get_or_create_shared_http() -> httpx.AsyncClient:
    """Return the process-wide shared ``httpx.AsyncClient``, creating it lazily."""
    global _shared_http
    with _LOCK:
        if _shared_http is None:
            _shared_http = httpx.AsyncClient(
                base_url=BaseClient.BASE_URL,
                timeout=BaseClient.REQUEST_TIMEOUT,
            )
        return _shared_http


def get_client(cls: type[T]) -> T:
    """Return a pooled client for the given class.

    For ``AuthClient`` subclasses, returns a fresh wrapper per call so each
    tool invocation re-reads ``auth_token.json`` from disk; the wrapper
    shares the process-wide ``httpx.AsyncClient`` via ``enable_pooling()``.
    For all other ``BaseClient`` subclasses, returns a cached singleton
    wrapper wired to the same shared ``httpx.AsyncClient``.
    """
    # When server tests patch a client class at its import site (e.g.
    # ``patch("server.comments.tools.MovieCommentsClient")``), ``cls`` is
    # a ``MagicMock`` instance rather than a class. ``issubclass(mock,
    # AuthClient)`` would raise ``TypeError``, so short-circuit to
    # ``cls()`` and let the mock's call semantics take over.
    if not inspect.isclass(cls):
        return cls()

    if issubclass(cls, AuthClient):
        instance = cls()
        instance.enable_pooling()
        return instance

    with _LOCK:
        cached = _CACHE.get(cls)
        if _is_instance_of(cached, cls):
            return cached
        instance = cls()
        instance.enable_pooling()
        _CACHE[cls] = instance
        return instance


async def shutdown_clients() -> None:
    """Close all pooled HTTP state. Call on process shutdown."""
    global _shared_http
    with _LOCK:
        _CACHE.clear()
        shared = _shared_http
        _shared_http = None
    if shared is not None:
        await shared.aclose()
