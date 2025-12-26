"""Post schemas for API validation."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional
from app.schemas.images import Images


class PostBase(BaseModel):
    """Base post schema."""

    name: str
    title: str
    text: str
    is_active: bool = True


class PostCreate(PostBase):
    """Post creation schema."""

    pass


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
