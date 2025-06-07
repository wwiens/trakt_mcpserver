from models import FormatHelper
import time

class TestFormatHelper:
    """Tests for the FormatHelper class in models.py"""
    
    def test_format_trending_shows(self):
        sample_data = [
            {
                "watchers": 100,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
                }
            },
            {
                "watchers": 80,
                "show": {
                    "title": "Stranger Things",
                    "year": 2016,
                    "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
                }
            }
        ]
        
        result = FormatHelper.format_trending_shows(sample_data)
        
        assert "# Trending Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "100 watchers" in result
        assert "Stranger Things (2016)" in result
        assert "80 watchers" in result
        assert "A high school chemistry teacher" in result
        assert "When a young boy disappears" in result
    
    def test_format_popular_shows(self):
        sample_data = [
            {
                "title": "Breaking Bad",
                "year": 2008,
                "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
            },
            {
                "title": "Stranger Things",
                "year": 2016,
                "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
            }
        ]
        
        result = FormatHelper.format_popular_shows(sample_data)
        
        assert "# Popular Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Stranger Things (2016)" in result
        assert "A high school chemistry teacher" in result
        assert "When a young boy disappears" in result
    
    def test_format_favorited_shows(self):
        sample_data = [
            {
                "user_count": 500,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
                }
            },
            {
                "user_count": 400,
                "show": {
                    "title": "Stranger Things",
                    "year": 2016,
                    "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
                }
            }
        ]
        
        result = FormatHelper.format_favorited_shows(sample_data)
        
        assert "# Most Favorited Shows on Trakt" in result
        assert "Breaking Bad (2008)" in result
        assert "Favorited by 500 users" in result
        assert "Stranger Things (2016)" in result
        assert "Favorited by 400 users" in result
    
    def test_format_played_shows(self):
        """Test formatting played shows data."""
        sample_data = [
            {
                "watcher_count": 300,
                "play_count": 1000,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
                }
            },
            {
                "watcher_count": 250,
                "play_count": 800,
                "show": {
                    "title": "Stranger Things",
                    "year": 2016,
                    "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
                }
            }
        ]
        
        result = FormatHelper.format_played_shows(sample_data)
        
        # Check title is present
        assert "# Most Played Shows on Trakt" in result
        
        # Check both shows are included with counts
        assert "Breaking Bad (2008)" in result
        assert "300 watchers, 1000 plays" in result
        assert "Stranger Things (2016)" in result
        assert "250 watchers, 800 plays" in result
    
    def test_format_watched_shows(self):
        """Test formatting watched shows data."""
        sample_data = [
            {
                "watcher_count": 300,
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
                }
            },
            {
                "watcher_count": 250,
                "show": {
                    "title": "Stranger Things",
                    "year": 2016,
                    "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
                }
            }
        ]
        
        result = FormatHelper.format_watched_shows(sample_data)
        
        # Check title is present
        assert "# Most Watched Shows on Trakt" in result
        
        # Check both shows are included with watcher counts
        assert "Breaking Bad (2008)" in result
        assert "Watched by 300 users" in result
        assert "Stranger Things (2016)" in result
        assert "Watched by 250 users" in result
    
    def test_format_trending_movies(self):
        """Test formatting trending movies data."""
        sample_data = [
            {
                "watchers": 150,
                "movie": {
                    "title": "Inception",
                    "year": 2010,
                    "overview": "A thief who steals corporate secrets through dream-sharing technology."
                }
            },
            {
                "watchers": 120,
                "movie": {
                    "title": "The Dark Knight",
                    "year": 2008,
                    "overview": "When the menace known as the Joker wreaks havoc on Gotham."
                }
            }
        ]
        
        result = FormatHelper.format_trending_movies(sample_data)
        
        # Check title is present
        assert "# Trending Movies on Trakt" in result
        
        # Check both movies are included
        assert "Inception (2010)" in result
        assert "150 watchers" in result
        assert "The Dark Knight (2008)" in result
        assert "120 watchers" in result
        
        # Check overviews are included
        assert "A thief who steals corporate secrets" in result
        assert "When the menace known as the Joker" in result
    
    def test_format_auth_status_authenticated(self):
        """Test formatting authentication status when authenticated."""
        current_time = int(time.time()) + 3600  # 1 hour from now
        result = FormatHelper.format_auth_status(True, current_time)
        
        assert "# Authentication Status" in result
        assert "You are authenticated with Trakt" in result
        assert str(current_time) in result
    
    def test_format_auth_status_not_authenticated(self):
        """Test formatting authentication status when not authenticated."""
        result = FormatHelper.format_auth_status(False)
        
        assert "# Authentication Status" in result
        assert "You are not authenticated with Trakt" in result
        assert "start_device_auth" in result
    
    def test_format_device_auth_instructions(self):
        """Test formatting device authentication instructions."""
        user_code = "ABC123"
        verification_url = "https://trakt.tv/activate"
        expires_in = 600  # 10 minutes
        
        result = FormatHelper.format_device_auth_instructions(user_code, verification_url, expires_in)
        
        assert "# Trakt Authentication Required" in result
        assert verification_url in result
        assert user_code in result
        assert "10 minutes" in result
    
    def test_format_user_watched_shows(self):
        """Test formatting user watched shows data."""
        sample_data = [
            {
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer."
                },
                "last_watched_at": "2023-01-15T20:30:00Z",
                "plays": 5
            },
            {
                "show": {
                    "title": "Stranger Things",
                    "year": 2016,
                    "overview": "When a young boy disappears, his mother and friends must confront terrifying forces."
                },
                "last_watched_at": "2023-02-20T18:45:00Z",
                "plays": 3
            }
        ]
        
        result = FormatHelper.format_user_watched_shows(sample_data)
        
        # Check title is present
        assert "# Your Watched Shows on Trakt" in result
        
        # Check both shows are included with watch info
        assert "Breaking Bad (2008)" in result
        assert "2023-01-15" in result
        assert "Plays: 5" in result
        assert "Stranger Things (2016)" in result
        assert "2023-02-20" in result
        assert "Plays: 3" in result
    
    def test_format_user_watched_shows_empty(self):
        """Test formatting user watched shows when empty."""
        result = FormatHelper.format_user_watched_shows([])
        
        assert "# Your Watched Shows on Trakt" in result
        assert "You haven't watched any shows yet" in result
    
    def test_format_show_search_results(self):
        """Test formatting show search results."""
        sample_data = [
            {
                "show": {
                    "title": "Breaking Bad",
                    "year": 2008,
                    "overview": "A high school chemistry teacher diagnosed with inoperable lung cancer.",
                    "ids": {"trakt": "1"}
                }
            },
            {
                "show": {
                    "title": "Better Call Saul",
                    "year": 2015,
                    "overview": "The trials and tribulations of criminal lawyer Jimmy McGill.",
                    "ids": {"trakt": "2"}
                }
            }
        ]
        
        result = FormatHelper.format_show_search_results(sample_data)
        
        # Check title is present
        assert "# Show Search Results" in result
        
        # Check both shows are included with IDs
        assert "Breaking Bad (2008)" in result
        assert "ID: 1" in result
        assert "Better Call Saul (2015)" in result
        assert "ID: 2" in result
        
        # Check tip for using search results
        assert "To check in to a show" in result
    
    def test_format_show_search_results_empty(self):
        """Test formatting show search results when empty."""
        result = FormatHelper.format_show_search_results([])
        
        assert "# Show Search Results" in result
        assert "No shows found matching your query" in result
    
    def test_format_show_ratings(self):
        """Test formatting show ratings."""
        sample_data = {
            "rating": 8.5,
            "votes": 1000,
            "distribution": {
                "10": 200,
                "9": 300,
                "8": 250,
                "7": 150,
                "6": 50,
                "5": 30,
                "4": 10,
                "3": 5,
                "2": 3,
                "1": 2
            }
        }
        
        result = FormatHelper.format_show_ratings(sample_data, "Breaking Bad")
        
        # Check title is present
        assert "# Ratings for Breaking Bad" in result
        
        # Check average rating and votes
        assert "**Average Rating:** 8.50/10" in result
        assert "from 1000 votes" in result
        
        # Check distribution table
        assert "| Rating | Votes | Percentage |" in result
        assert "| 10/10 | 200 | 20.0% |" in result
        assert "| 9/10 | 300 | 30.0% |" in result
    
    def test_format_comments(self):
        """Test formatting comments."""
        sample_data = [
            {
                "user": {"username": "user1"},
                "created_at": "2023-01-15T20:30:00Z",
                "comment": "This is a great show!",
                "spoiler": False,
                "review": False,
                "replies": 2,
                "likes": 10,
                "id": "123"
            },
            {
                "user": {"username": "user2"},
                "created_at": "2023-01-16T10:15:00Z",
                "comment": "I didn't like the ending.",
                "spoiler": True,
                "review": False,
                "replies": 1,
                "likes": 5,
                "id": "124"
            }
        ]
        
        # Test without showing spoilers
        result = FormatHelper.format_comments(sample_data, "Breaking Bad", show_spoilers=False)
        
        # Check title is present
        assert "# Comments for Breaking Bad" in result
        
        # Check non-spoiler comment is shown
        assert "user1" in result
        assert "2023-01-15" in result
        assert "This is a great show!" in result
        assert "Likes: 10 | Replies: 2" in result
        
        # Check spoiler comment is hidden
        assert "user2" in result
        assert "SPOILER WARNING" in result
        assert "I didn't like the ending." not in result
        
        # Test with showing spoilers
        result = FormatHelper.format_comments(sample_data, "Breaking Bad", show_spoilers=True)
        
        # Check spoiler comment is now shown
        assert "user2" in result
        assert "I didn't like the ending." in result
        
    def test_format_comment(self):
        """Test formatting a single comment."""
        sample_comment = {
            "user": {"username": "reviewer"},
            "created_at": "2023-03-10T14:25:00Z",
            "comment": "This is my detailed review of the show.",
            "spoiler": False,
            "review": True,
            "replies": 5,
            "likes": 20,
            "id": "456"
        }
        
        result = FormatHelper.format_comment(sample_comment)
        
        # Check title and metadata
        assert "# Comment by reviewer [REVIEW]" in result
        assert "**Posted:** 2023-03-10 14:25:00" in result
        assert "This is my detailed review of the show." in result
        assert "Likes: 20 | Replies: 5 | ID: 456" in result
        
    def test_format_comment_with_replies(self):
        """Test formatting a comment with its replies."""
        sample_comment = {
            "user": {"username": "mainuser"},
            "created_at": "2023-04-05T09:15:00Z",
            "comment": "What did everyone think of the finale?",
            "spoiler": False,
            "review": False,
            "replies": 2,
            "likes": 8,
            "id": "789"
        }
        
        sample_replies = [
            {
                "user": {"username": "reply1"},
                "created_at": "2023-04-05T10:30:00Z",
                "comment": "I loved it!",
                "spoiler": False,
                "review": False,
                "id": "790"
            },
            {
                "user": {"username": "reply2"},
                "created_at": "2023-04-05T11:45:00Z",
                "comment": "The twist at the end was shocking.",
                "spoiler": True,
                "review": False,
                "id": "791"
            }
        ]
        
        # Test with showing spoilers
        result = FormatHelper.format_comment(
            sample_comment, 
            with_replies=True, 
            replies=sample_replies, 
            show_spoilers=True
        )
        
        # Check main comment
        assert "# Comment by mainuser" in result
        assert "What did everyone think of the finale?" in result
        
        # Check replies section
        assert "## Replies" in result
        assert "### reply1" in result
        assert "I loved it!" in result
        assert "### reply2 [SPOILER]" in result
        assert "The twist at the end was shocking." in result
        
        # Test without showing spoilers
        result = FormatHelper.format_comment(
            sample_comment, 
            with_replies=True, 
            replies=sample_replies, 
            show_spoilers=False
        )
        
        # Check spoiler reply is hidden
        assert "### reply2 [SPOILER]" in result
        assert "SPOILER WARNING" in result
        assert "The twist at the end was shocking." not in result
        
    def test_format_movie_search_results(self):
        """Test formatting movie search results."""
        sample_data = [
            {
                "movie": {
                    "title": "Inception",
                    "year": 2010,
                    "overview": "A thief who steals corporate secrets through dream-sharing technology.",
                    "ids": {"trakt": "1"}
                }
            },
            {
                "movie": {
                    "title": "Interstellar",
                    "year": 2014,
                    "overview": "A team of explorers travel through a wormhole in space.",
                    "ids": {"trakt": "2"}
                }
            }
        ]
        
        result = FormatHelper.format_movie_search_results(sample_data)
        
        # Check title is present
        assert "# Movie Search Results" in result
        
        # Check both movies are included with IDs
        assert "Inception (2010)" in result
        assert "ID: 1" in result
        assert "Interstellar (2014)" in result
        assert "ID: 2" in result
        
        # Check tip for using search results
        assert "To view comments for a movie" in result
        
    def test_format_movie_search_results_empty(self):
        """Test formatting movie search results when empty."""
        result = FormatHelper.format_movie_search_results([])
        
        assert "# Movie Search Results" in result
        assert "No movies found matching your query" in result
        
    def test_format_movie_ratings(self):
        """Test formatting movie ratings."""
        sample_data = {
            "rating": 9.0,
            "votes": 2000,
            "distribution": {
                "10": 800,
                "9": 600,
                "8": 300,
                "7": 150,
                "6": 80,
                "5": 40,
                "4": 20,
                "3": 5,
                "2": 3,
                "1": 2
            }
        }
        
        result = FormatHelper.format_movie_ratings(sample_data, "Inception")
        
        # Check title is present
        assert "# Ratings for Inception" in result
        
        # Check average rating and votes
        assert "**Average Rating:** 9.00/10" in result
        assert "from 2000 votes" in result
        
        # Check distribution table
        assert "| Rating | Votes | Percentage |" in result
        assert "| 10/10 | 800 | 40.0% |" in result
        assert "| 9/10 | 600 | 30.0% |" in result
        
    def test_format_checkin_response(self):
        """Test formatting checkin response."""
        sample_data = {
            "id": 123456,
            "watched_at": "2023-05-10T20:30:00Z",
            "sharing": {
                "twitter": True,
                "mastodon": False,
                "tumblr": False
            },
            "show": {
                "title": "Breaking Bad",
                "year": 2008
            },
            "episode": {
                "season": 1,
                "number": 1,
                "title": "Pilot"
            }
        }
        
        result = FormatHelper.format_checkin_response(sample_data)
        
        # Check title and show info
        assert "# Successfully Checked In" in result
        assert "Breaking Bad" in result
        assert "S01E01: Pilot" in result
        
        # Check timestamp and sharing info
        assert "2023-05-10 20:30:00" in result
        assert "Shared on: Twitter" in result
        assert "Checkin ID: 123456" in result
