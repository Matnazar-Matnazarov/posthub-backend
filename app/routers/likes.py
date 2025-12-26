"""Likes router endpoints."""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.likes import Likes, LikesCreate, LikesToggle, LikesStats
from app.crud.likes import create_like, get_like, toggle_like, get_likes_stats
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.post import Post

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/{post_id}", response_model=Likes, status_code=status.HTTP_201_CREATED)
async def create_new_like(
    post_id: int,
    like: LikesCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new like on a post."""
    if not await Post.filter(id=post_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    try:
        return await create_like(like, current_user.id, post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{post_id}/toggle", response_model=LikesToggle)
async def toggle_post_like(
    post_id: int,
    is_like: bool = True,
    current_user: User = Depends(get_current_user),
):
    """Toggle like/dislike on a post. If already liked/disliked with same value, removes it."""
    if not await Post.filter(id=post_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    try:
        liked, likes_count, dislikes_count = await toggle_like(
            current_user.id, post_id, is_like
        )
        return LikesToggle(
            liked=liked,
            likes_count=likes_count,
            dislikes_count=dislikes_count
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{post_id}/stats", response_model=LikesStats)
async def get_post_likes_stats(
    post_id: int,
    current_user: User = Depends(get_current_user),
):
    """Get likes statistics for a post."""
    if not await Post.filter(id=post_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    return await get_likes_stats(post_id, current_user.id)


@router.get("/{like_id}", response_model=Likes)
async def read_like(like_id: int, current_user: User = Depends(get_current_user)):
    """Get a like by ID."""
    db_like = await get_like(like_id)
    if db_like is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Like not found"
        )
    if db_like.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to view this like",
        )
    return db_like
