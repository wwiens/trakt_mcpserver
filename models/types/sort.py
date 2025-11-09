"""Sort parameter types for Trakt API endpoints."""

from typing import Literal

# Comment sort types based on Trakt API documentation
CommentSortBasic = Literal["newest", "oldest", "likes", "replies"]
CommentSortExtended = Literal[
    "newest", "oldest", "likes", "replies", "highest", "lowest", "plays"
]
CommentSortFull = Literal[
    "newest",
    "oldest",
    "likes",
    "replies",
    "highest",
    "lowest",
    "plays",
    "watched",
]

# Specific sort types for each endpoint (from trakt.apib)
MovieCommentSort = (
    CommentSortExtended  # newest, oldest, likes, replies, highest, lowest, plays
)
ShowCommentSort = CommentSortFull  # adds 'watched' percentage
SeasonCommentSort = CommentSortFull  # adds 'watched' percentage
EpisodeCommentSort = (
    CommentSortExtended  # newest, oldest, likes, replies, highest, lowest, plays
)
