"""Tests for server bootstrap behavior in server.main."""

import logging
from collections.abc import Generator
from importlib.metadata import PackageNotFoundError

import pytest

import server.main as main_module


@pytest.fixture
def trakt_mcp_caplog(
    caplog: pytest.LogCaptureFixture,
) -> Generator[pytest.LogCaptureFixture, None, None]:
    """Attach caplog's handler to the trakt_mcp logger.

    The project disables propagation on the trakt_mcp logger via
    utils.api.structured_logging.get_structured_logger, so caplog's
    root-attached handler does not see its records by default.
    """
    logger = logging.getLogger("trakt_mcp")
    logger.addHandler(caplog.handler)
    original_level = logger.level
    logger.setLevel(logging.INFO)
    try:
        yield caplog
    finally:
        logger.removeHandler(caplog.handler)
        logger.setLevel(original_level)


def test_create_server_falls_back_when_package_metadata_missing(
    monkeypatch: pytest.MonkeyPatch, trakt_mcp_caplog: pytest.LogCaptureFixture
) -> None:
    """When importlib.metadata cannot find the distribution, the logged version
    is the '0.0.0+dev' fallback rather than raising."""

    def _raise(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(main_module, "_pkg_version", _raise)

    main_module.create_server()

    assert any(
        "v0.0.0+dev" in record.getMessage() for record in trakt_mcp_caplog.records
    ), "expected fallback version 'v0.0.0+dev' in startup log"


def test_create_server_logs_resolved_version_when_package_present(
    monkeypatch: pytest.MonkeyPatch, trakt_mcp_caplog: pytest.LogCaptureFixture
) -> None:
    """When the distribution is installed, the logged version comes from
    importlib.metadata.version, not the fallback."""

    def _fixed_version(_name: str) -> str:
        return "1.2.3"

    monkeypatch.setattr(main_module, "_pkg_version", _fixed_version)

    main_module.create_server()

    messages = [record.getMessage() for record in trakt_mcp_caplog.records]
    assert any("v1.2.3" in message for message in messages)
    assert not any("0.0.0+dev" in message for message in messages)
