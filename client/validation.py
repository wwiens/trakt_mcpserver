"""Shared validation utilities for client modules."""


def validate_media_id(media_id: str, field_name: str = "id") -> str:
    """Strip and validate a media ID, returning the stripped value.

    Args:
        media_id: The media identifier to validate
        field_name: Name of the field for error messages

    Returns:
        Stripped media_id

    Raises:
        ValueError: If media_id is empty after stripping
    """
    media_id = media_id.strip()
    if not media_id:
        msg = f"{field_name} cannot be empty"
        raise ValueError(msg)
    return media_id
