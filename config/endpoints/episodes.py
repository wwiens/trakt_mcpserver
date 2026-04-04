"""Episode endpoints."""

from typing import Final

EPISODES_ENDPOINTS: Final[dict[str, str]] = {
    "episode_summary": "/shows/:id/seasons/:season/episodes/:episode",
    "episode_translations": (
        "/shows/:id/seasons/:season/episodes/:episode/translations/:language"
    ),
    "episode_lists": "/shows/:id/seasons/:season/episodes/:episode/lists/:type/:sort",
    "episode_people": "/shows/:id/seasons/:season/episodes/:episode/people",
    "episode_ratings": "/shows/:id/seasons/:season/episodes/:episode/ratings",
    "episode_stats": "/shows/:id/seasons/:season/episodes/:episode/stats",
    "episode_watching": "/shows/:id/seasons/:season/episodes/:episode/watching",
    "episode_videos": "/shows/:id/seasons/:season/episodes/:episode/videos",
}
