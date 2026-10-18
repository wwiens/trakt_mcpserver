"""Tests for the package version helper."""

from collections.abc import Generator
from importlib.metadata import PackageNotFoundError

import pytest

from utils import version as version_module


@pytest.fixture(autouse=True)
def clear_version_cache() -> Generator[None, None, None]:
    version_module.package_version.cache_clear()
    yield
    version_module.package_version.cache_clear()


def test_package_version_reads_installed_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    looked_up: list[str] = []

    def _fixed_version(name: str) -> str:
        looked_up.append(name)
        return "1.2.3"

    monkeypatch.setattr(version_module, "_pkg_version", _fixed_version)

    assert version_module.package_version() == "1.2.3"
    assert looked_up == [version_module.PACKAGE_NAME]


def test_package_version_falls_back_when_not_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _raise(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr(version_module, "_pkg_version", _raise)

    assert version_module.package_version() == version_module.UNINSTALLED_VERSION


def test_package_version_is_looked_up_once(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    def _counting_version(name: str) -> str:
        calls.append(name)
        return "1.2.3"

    monkeypatch.setattr(version_module, "_pkg_version", _counting_version)

    version_module.package_version()
    version_module.package_version()

    assert len(calls) == 1
