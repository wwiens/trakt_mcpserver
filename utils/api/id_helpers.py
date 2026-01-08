"""Helpers for building Trakt ID objects."""


def build_trakt_id_object(
    item_id: str, item_type: str
) -> dict[str, list[dict[str, dict[str, str | int]]]]:
    """Build a Trakt API ID object for POST requests.

    Args:
        item_id: Trakt ID (numeric), slug, or IMDB ID (starts with 'tt').
        item_type: Type of item ('movies' or 'shows').

    Returns:
        Dictionary formatted for Trakt API requests, e.g.:
        {"movies": [{"ids": {"trakt": 123}}]} or
        {"shows": [{"ids": {"imdb": "tt1234567"}}]}
    """
    if item_id.isdigit():
        id_obj: dict[str, str | int] = {"trakt": int(item_id)}
    elif item_id.startswith("tt"):
        id_obj = {"imdb": item_id}
    else:
        id_obj = {"slug": item_id}

    return {item_type: [{"ids": id_obj}]}
