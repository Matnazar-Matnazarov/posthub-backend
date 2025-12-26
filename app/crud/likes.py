"""Likes CRUD operations."""

from typing import Optional, Tuple
from app.models.likes import Likes
from app.schemas.likes import LikesCreate, LikesStats
from app.models.post import Post


async def create_like(like: LikesCreate, user_id: int, post_id: int) -> Likes:
    """Create a new like."""
    if not await Post.filter(id=post_id).exists():
        raise ValueError("Post not found")

    if await Likes.filter(user_id=user_id, post_id=post_id).exists():
        raise ValueError("User has already liked this post")

    db_like = Likes(**like.model_dump(), user_id=user_id, post_id=post_id)
    await db_like.save()
    return db_like


async def get_like(like_id: int) -> Optional[Likes]:
    """Get a like by ID."""
    return await Likes.get_or_none(id=like_id)


async def get_user_like(user_id: int, post_id: int) -> Optional[Likes]:
    """Get user's like for a post."""
    return await Likes.get_or_none(user_id=user_id, post_id=post_id)


async def toggle_like(user_id: int, post_id: int, is_like: bool = True) -> Tuple[bool, int, int]:
    """Toggle like/dislike on a post. Returns (liked, likes_count, dislikes_count)."""
    if not await Post.filter(id=post_id).exists():
        raise ValueError("Post not found")
    
    existing = await Likes.get_or_none(user_id=user_id, post_id=post_id)
    
    if existing:
        if existing.is_like == is_like:
            # Same action - remove the like/dislike
            await existing.delete()
            liked = False
        else:
            # Different action - switch between like/dislike
            existing.is_like = is_like
            await existing.save()
            liked = True
    else:
        # Create new like
        new_like = Likes(user_id=user_id, post_id=post_id, is_like=is_like)
        await new_like.save()
        liked = True
    
    # Get updated counts
    likes_count = await Likes.filter(post_id=post_id, is_like=True).count()
    dislikes_count = await Likes.filter(post_id=post_id, is_like=False).count()
    
    return liked, likes_count, dislikes_count


async def delete_like(user_id: int, post_id: int) -> bool:
    """Delete a like."""
    like = await Likes.get_or_none(user_id=user_id, post_id=post_id)
    if like:
        await like.delete()
        return True
    return False


async def get_likes_stats(post_id: int, user_id: Optional[int] = None) -> LikesStats:
    """Get likes statistics for a post."""
    likes_count = await Likes.filter(post_id=post_id, is_like=True).count()
    dislikes_count = await Likes.filter(post_id=post_id, is_like=False).count()
    
    user_liked = None
    if user_id:
        user_like = await Likes.get_or_none(user_id=user_id, post_id=post_id)
        if user_like:
            user_liked = user_like.is_like
    
    return LikesStats(
        likes_count=likes_count,
        dislikes_count=dislikes_count,
        user_liked=user_liked
    )
