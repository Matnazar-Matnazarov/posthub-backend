"""Comment schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime


class CommentBase(BaseModel):
    """Base comment schema."""

    comment: str
    is_active: bool = True


class CommentCreate(CommentBase):
    """Comment creation schema."""

    pass


class Comment(CommentBase):
    """Comment response schema."""

    id: int
    user_id: int
    post_id: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)
