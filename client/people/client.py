"""Unified people client that combines all person functionality."""

from .lists import PersonListsClient
from .movies import PersonMoviesClient
from .shows import PersonShowsClient
from .summary import PersonSummaryClient


class PeopleClient(
    PersonSummaryClient,
    PersonMoviesClient,
    PersonShowsClient,
    PersonListsClient,
):
    """Unified client for all people-related operations.

    Combines functionality from:
    - PersonSummaryClient: get_person(), get_person_extended()
    - PersonMoviesClient: get_person_movies()
    - PersonShowsClient: get_person_shows()
    - PersonListsClient: get_person_lists()
    """

    pass
