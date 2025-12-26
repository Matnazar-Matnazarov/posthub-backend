"""Comment schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List


class CommentBase(BaseModel):
    """Base comment schema."""

    comment: str
    is_active: bool = True


class CommentCreate(CommentBase):
    """Comment creation schema."""
    
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    """Comment update schema."""
    
    comment: Optional[str] = None
    is_active: Optional[bool] = None


class CommentUser(BaseModel):
    """User info for comment."""
    
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Comment(CommentBase):
    """Comment response schema."""

    id: int
    user_id: int
    post_id: int
    parent_id: Optional[int] = None
    created: datetime
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CommentWithUser(Comment):
    """Comment with user info."""
    
    user: Optional[CommentUser] = None
    replies: List["CommentWithUser"] = []
    likes_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


# Update forward references
CommentWithUser.model_rebuild()
