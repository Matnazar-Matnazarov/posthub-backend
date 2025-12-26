"""Post view schemas."""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class PostViewCreate(BaseModel):
    """Create post view."""
    
    pass


class PostView(BaseModel):
    """Post view response."""
    
    id: int
    post_id: int
    user_id: Optional[int] = None
    ip_address: str
    created: datetime
    
    model_config = ConfigDict(from_attributes=True)


class PostViewStats(BaseModel):
    """Post view statistics."""
    
    total_views: int = 0
    unique_views: int = 0

