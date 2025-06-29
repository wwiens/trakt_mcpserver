# Modular Models Tests

This directory contains the modernized, modular test structure for the models package, mirroring the models/ directory architecture.

## Structure

- `test_auth.py` - Tests for `models.auth` module (TraktAuthToken, TraktDeviceCode)
- `test_media.py` - Tests for `models.media` module (TraktShow, TraktMovie, TraktEpisode, etc.)
- `test_user.py` - Tests for `models.user` module (TraktUserShow)  
- `test_formatters.py` - Tests for `models.formatters` module (FormatHelper class)

## Test Coverage

### Authentication Models (test_auth.py)
- **TraktDeviceCode**: Creation, validation, serialization, field types
- **TraktAuthToken**: Creation, validation, serialization, expiration logic, API response handling

### Media Models (test_media.py)
- **TraktShow**: Basic show data, validation, serialization
- **TraktMovie**: Basic movie data, validation, serialization  
- **TraktEpisode**: Episode data with season/number validation
- **TraktTrendingShow/Movie**: Trending data with watchers count
- **TraktPopularShow/Movie**: Popular data with `from_api_response` methods
- **Integration tests**: Complex data structures and model interactions

### User Models (test_user.py)
- **TraktUserShow**: User show data with watch history, seasons, validation
- **API response handling**: Converting real API responses to model instances
- **Complex seasons data**: Nested episode data structures

### Formatters (test_formatters.py)
- **FormatHelper**: All formatting methods for shows, movies, auth status
- **Search results**: Show/movie search formatting with IDs
- **Comments**: Comment formatting with spoiler handling
- **Ratings**: Rating distribution tables and calculations
- **Error handling**: Malformed data graceful handling

## Key Features

- **Comprehensive validation testing** using clearly incompatible types to ensure Pydantic validation works
- **Serialization/deserialization** round-trip testing for all models
- **Real API response simulation** to ensure models work with actual Trakt API data
- **Edge case handling** including empty data, malformed inputs, and error conditions
- **Integration testing** showing how models work together in complex scenarios

## Running Tests

```bash
# Run all modular model tests
pytest tests/models_new/ -v

# Run specific test file
pytest tests/models_new/test_auth.py -v

# Run alongside existing tests
pytest tests/models/ tests/models_new/ -v
```

## Migration Status

This new modular structure complements the existing `tests/models/test_format_helper.py` and provides complete coverage of the models package with a structure that mirrors the actual codebase organization.

Total tests: 101 tests covering all model classes and functionality.