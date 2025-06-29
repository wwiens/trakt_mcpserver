"""Integration tests for config constants direct imports."""

# Test imports from domain-specific config modules
from config.api import DEFAULT_LIMIT
from config.auth import AUTH_EXPIRATION, AUTH_POLL_INTERVAL, AUTH_VERIFICATION_URL


class TestDirectImports:
    """Test that constants can be imported from domain-specific config modules."""

    def test_auth_constants_importable_from_domain_modules(self) -> None:
        """Test auth constants can be imported from main config module."""
        # These imports should work without error
        assert AUTH_POLL_INTERVAL is not None
        assert AUTH_EXPIRATION is not None
        assert AUTH_VERIFICATION_URL is not None

    def test_api_constants_importable_from_main_config(self) -> None:
        """Test API constants can be imported from main config module."""
        # This import should work without error
        assert DEFAULT_LIMIT is not None

    def test_auth_constants_have_correct_values(self) -> None:
        """Test auth constants have expected values when imported from main config."""
        assert AUTH_POLL_INTERVAL == 5
        assert AUTH_EXPIRATION == 600
        assert AUTH_VERIFICATION_URL == "https://trakt.tv/activate"

    def test_api_constants_have_correct_values(self) -> None:
        """Test API constants have expected values when imported from main config."""
        assert DEFAULT_LIMIT == 10

    def test_constants_match_domain_modules(self) -> None:
        """Test that constants from main config match those from domain modules."""
        # Import from domain-specific modules
        from config.api.constants import DEFAULT_LIMIT as DEFAULT_LIMIT_DOMAIN
        from config.auth.constants import AUTH_EXPIRATION as AUTH_EXP_DOMAIN
        from config.auth.constants import AUTH_POLL_INTERVAL as AUTH_POLL_DOMAIN
        from config.auth.constants import AUTH_VERIFICATION_URL as AUTH_URL_DOMAIN

        # Should be identical
        assert AUTH_EXPIRATION == AUTH_EXP_DOMAIN
        assert AUTH_POLL_INTERVAL == AUTH_POLL_DOMAIN
        assert AUTH_VERIFICATION_URL == AUTH_URL_DOMAIN
        assert DEFAULT_LIMIT == DEFAULT_LIMIT_DOMAIN

    def test_constants_integration_relationships(self) -> None:
        """Test integration relationships between constants still work."""
        # Expiration should be at least 10 times the poll interval
        assert AUTH_EXPIRATION >= AUTH_POLL_INTERVAL * 10
        # This ensures reasonable number of polling attempts
        max_polls = AUTH_EXPIRATION // AUTH_POLL_INTERVAL
        assert max_polls >= 10  # At least 10 polling attempts possible

    def test_all_constants_are_immutable_types(self) -> None:
        """Test that all constants use immutable types."""
        constants = [
            AUTH_POLL_INTERVAL,
            AUTH_EXPIRATION,
            AUTH_VERIFICATION_URL,
            DEFAULT_LIMIT,
        ]

        for constant in constants:
            # Should be one of the basic immutable types
            assert isinstance(constant, int | str | float | bool | tuple)
