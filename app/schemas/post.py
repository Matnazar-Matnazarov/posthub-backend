"""Post schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.schemas.images import Images
from app.schemas.comment import CommentWithUser
from app.schemas.likes import LikesStats


class PostBase(BaseModel):
    """Base post schema."""

    name: str
    title: str
    text: str
    is_active: bool = True


class PostCreate(PostBase):
    """Post creation schema."""

    pass


class PostUpdate(BaseModel):
    """Post update schema."""
    
    name: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    is_active: Optional[bool] = None


class PostUser(BaseModel):
    """User info for post."""
    
    id: int
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class Post(PostBase):
    """Post response schema."""

    id: int
    user_id: int
    created: datetime
    updated: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class PostImage(PostBase):
    """Post with images response schema."""

    id: int
    user_id: int
    created: datetime
    updated: Optional[datetime] = None
    images: List[Images] = []

    model_config = ConfigDict(from_attributes=True)


class PostList(BaseModel):
    """Post list item for public view."""
    
    id: int
    name: str
    title: str
    text: str
    user_id: int
    user: Optional[PostUser] = None
    created: datetime
    updated: Optional[datetime] = None
    images: List[Images] = []
    likes_count: int = 0
    dislikes_count: int = 0
    comments_count: int = 0
    views_count: int = 0
    
    model_config = ConfigDict(from_attributes=True)


class PostDetail(PostList):
    """Post detail with full info."""
    
    comments: List[CommentWithUser] = []
    likes: LikesStats = LikesStats()
    user_liked: Optional[bool] = None
    is_owner: bool = False
    
    model_config = ConfigDict(from_attributes=True)
