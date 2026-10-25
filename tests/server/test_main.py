"""Tests for server bootstrap behavior in server.main."""

import logging
from collections.abc import Generator

import pytest

import server.main as main_module
from utils.version import UNINSTALLED_VERSION


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

    monkeypatch.setattr(main_module, "package_version", lambda: UNINSTALLED_VERSION)

    main_module.create_server()

    assert any(
        "v0.0.0+dev" in record.getMessage() for record in trakt_mcp_caplog.records
    ), "expected fallback version 'v0.0.0+dev' in startup log"


def test_create_server_logs_resolved_version_when_package_present(
    monkeypatch: pytest.MonkeyPatch, trakt_mcp_caplog: pytest.LogCaptureFixture
) -> None:
    """When the distribution is installed, the logged version comes from
    importlib.metadata.version, not the fallback."""

    monkeypatch.setattr(main_module, "package_version", lambda: "1.2.3")

    main_module.create_server()

    messages = [record.getMessage() for record in trakt_mcp_caplog.records]
    assert any("v1.2.3" in message for message in messages)
    assert not any("0.0.0+dev" in message for message in messages)
