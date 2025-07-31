"""Standardized error message constants for the Trakt MCP server."""

# Authentication error messages
AUTH_REQUIRED = "Authentication required. Use the 'start_device_auth' tool to authenticate with Trakt."
AUTH_REQUIRED_MARKDOWN = (
    "# Authentication required\n\n"
    "You need to authenticate with Trakt to access this resource.\n"
    "Use the `start_device_auth` tool to begin authentication."
)
AUTH_EXPIRED = (
    "Your authentication has expired. Please re-authenticate using 'start_device_auth'."
)
AUTH_INVALID = "Invalid authentication credentials. Please re-authenticate using 'start_device_auth'."

# Validation error messages
INVALID_PARAMETER = "Invalid {parameter}: {reason}"
MISSING_PARAMETER = "Missing required parameter: {parameter}"
EMPTY_QUERY = "Search query cannot be empty. Please provide a search term."
INVALID_ID = "Invalid {resource_type} ID: {id}. Must be a valid Trakt ID."

# Resource not found messages
RESOURCE_NOT_FOUND = "Resource not found: {resource_type} with {identifier}"
SHOW_NOT_FOUND = "Show not found with ID: {show_id}"
MOVIE_NOT_FOUND = "Movie not found with ID: {movie_id}"
USER_NOT_FOUND = "User not found: {username}"

# API error messages
API_UNAVAILABLE = "Invalid response format from Trakt API. Please try again later."
RATE_LIMITED = "Rate limit exceeded. Please try again later."
NETWORK_ERROR = "Unable to connect to Trakt API. Please check your internet connection."
BAD_REQUEST = "Bad request. Please check your request parameters."
ACCESS_FORBIDDEN = (
    "Access forbidden. You don't have permission to access this resource."
)
UNPROCESSABLE_ENTITY = "Unprocessable entity. The request is syntactically correct but semantically invalid."

# User messages
NO_WATCHED_SHOWS = (
    "You haven't watched any shows yet, or you need to authenticate first."
)
NO_WATCHED_MOVIES = (
    "You haven't watched any movies yet, or you need to authenticate first."
)

# Validation patterns
VALID_TRAKT_ID_PATTERN = r"^\d+$"
VALID_USERNAME_PATTERN = r"^[a-zA-Z0-9_-]+$"
