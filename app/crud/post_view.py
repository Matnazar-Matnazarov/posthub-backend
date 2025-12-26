"""Post view CRUD operations."""

from typing import Optional
from datetime import datetime, timedelta
from app.models.post_view import PostView
from app.config import settings


async def record_view(
    post_id: int, 
    ip_address: str, 
    user_id: Optional[int] = None,
    user_agent: Optional[str] = None
) -> bool:
    """Record a post view. Returns True if new view, False if duplicate."""
    # Check for recent view from same IP or user (within 1 hour)
    one_hour_ago = datetime.now(settings.TIMEZONE) - timedelta(hours=1)
    
    if user_id:
        # For logged in users, check by user_id
        existing = await PostView.filter(
            post_id=post_id,
            user_id=user_id,
            created__gte=one_hour_ago
        ).exists()
    else:
        # For guests, check by IP
        existing = await PostView.filter(
            post_id=post_id,
            ip_address=ip_address,
            created__gte=one_hour_ago
        ).exists()
    
    if existing:
        return False
    
    # Create new view record
    view = PostView(
        post_id=post_id,
        ip_address=ip_address,
        user_id=user_id,
        user_agent=user_agent
    )
    await view.save()
    return True


async def get_view_count(post_id: int) -> int:
    """Get total view count for a post."""
    return await PostView.filter(post_id=post_id).count()


async def get_unique_view_count(post_id: int) -> int:
    """Get unique view count for a post (by IP)."""
    # Using distinct on ip_address
    views = await PostView.filter(post_id=post_id).values_list("ip_address", flat=True)
    return len(set(views))

