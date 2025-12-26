"""Likes schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class LikesBase(BaseModel):
    """Base likes schema."""

    is_like: bool = True


class LikesCreate(LikesBase):
    """Likes creation schema."""

    pass


class LikesToggle(BaseModel):
    """Like toggle response."""
    
    liked: bool
    likes_count: int
    dislikes_count: int


class Likes(LikesBase):
    """Likes response schema."""

    id: int
    user_id: int
    post_id: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class LikesStats(BaseModel):
    """Likes statistics for a post."""
    
    likes_count: int = 0
    dislikes_count: int = 0
    user_liked: Optional[bool] = None  # None if not logged in, True/False otherwise
