"""Package version lookup, read once from the installed distribution metadata."""

import functools
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _pkg_version
from typing import Final

PACKAGE_NAME: Final[str] = "trakt-mcp"
# Reported when running from a source tree that was never pip-installed.
UNINSTALLED_VERSION: Final[str] = "0.0.0+dev"


@functools.cache
def package_version() -> str:
    """Return the installed trakt-mcp version (pyproject.toml is the source)."""
    try:
        return _pkg_version(PACKAGE_NAME)
    except PackageNotFoundError:
        return UNINSTALLED_VERSION
