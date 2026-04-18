"""Process-wide pool of ``BaseClient`` instances and their shared ``httpx.AsyncClient``.

Non-authenticated client classes are cached as singletons per class and share
a single ``httpx.AsyncClient`` for connection reuse across all Trakt API
requests. ``AuthClient`` subclasses are *not* pooled: each call returns a
fresh instance, preserving the "disk is the source of truth" invariant for
authentication state (so login, refresh, and clear propagate consistently
across unrelated tool calls). Direct ``SomeClient()`` instantiation is
unaffected and still opens/closes a fresh HTTP client per request.
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
    """TypeGuard wrapper around ``isinstance`` that preserves the ``T`` binding."""
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

    For ``AuthClient`` subclasses, returns a fresh instance per call so
    each tool invocation re-reads ``auth_token.json`` from disk. For all
    other ``BaseClient`` subclasses, returns a cached singleton wired to
    the shared ``httpx.AsyncClient``.
    """
    # Tests that patch the client class name at the call site pass a
    # ``MagicMock`` here; skip all pooling so the mock's call semantics
    # stay intact.
    if not inspect.isclass(cls):
        return cls()

    if issubclass(cls, AuthClient):
        return cls()

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
