"""Likes schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class LikesBase(BaseModel):
    """Base likes schema."""

    is_like: bool = True


class LikesCreate(LikesBase):
    """Likes creation schema."""

    pass


class Likes(LikesBase):
    """Likes response schema."""

    id: int
    user_id: int
    post_id: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)
