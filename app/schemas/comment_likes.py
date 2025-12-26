"""Comment likes schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CommentLikesBase(BaseModel):
    """Base comment likes schema."""

    is_like: bool = True


class CommentLikesCreate(CommentLikesBase):
    """Comment likes creation schema."""

    pass


class CommentLikes(CommentLikesBase):
    """Comment likes response schema."""

    id: int
    user_id: int
    comment_id: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)
