"""Season endpoints."""

from collections.abc import Mapping
from typing import Final

from .keys import EndpointKey

SEASONS_ENDPOINTS: Final[Mapping[EndpointKey, str]] = {
    "season_info": "/shows/:id/seasons/:season/info",
    "season_episodes": "/shows/:id/seasons/:season",
    "season_ratings": "/shows/:id/seasons/:season/ratings",
    "season_stats": "/shows/:id/seasons/:season/stats",
    "season_people": "/shows/:id/seasons/:season/people",
    "season_videos": "/shows/:id/seasons/:season/videos",
    "season_watching": "/shows/:id/seasons/:season/watching",
    "season_translations": "/shows/:id/seasons/:season/translations/:language",
    "season_lists": "/shows/:id/seasons/:season/lists/:type/:sort",
}
