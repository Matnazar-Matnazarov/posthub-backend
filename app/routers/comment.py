"""Comment router endpoints."""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.comment import Comment, CommentCreate, CommentUpdate, CommentWithUser
from app.crud.comment import (
    create_comment, 
    get_comment, 
    update_comment, 
    delete_comment,
    get_post_comments,
    build_comment_tree
)
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.post import Post
from app.websocket import notify_new_comment

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/{post_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def create_new_comment(
    post_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new comment on a post."""
    post = await Post.get_or_none(id=post_id).prefetch_related("user")
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    try:
        new_comment = await create_comment(comment, current_user.id, post_id)
        
        # Notify post owner about new comment (don't notify self)
        if post.user_id != current_user.id:
            commenter_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username
            await notify_new_comment(
                post.user_id,
                post_id,
                post.title,
                commenter_name,
                comment.comment
            )
        
        return new_comment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{post_id}/reply/{parent_id}", response_model=Comment, status_code=status.HTTP_201_CREATED)
async def reply_to_comment(
    post_id: int,
    parent_id: int,
    comment: CommentCreate,
    current_user: User = Depends(get_current_user),
):
    """Reply to an existing comment."""
    if not await Post.filter(id=post_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    
    # Override parent_id from URL
    comment.parent_id = parent_id

    try:
        return await create_comment(comment, current_user.id, post_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/post/{post_id}", response_model=List[CommentWithUser])
async def get_comments_for_post(post_id: int):
    """Get all comments for a post (public endpoint)."""
    if not await Post.filter(id=post_id).exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    
    comments = await get_post_comments(post_id)
    return await build_comment_tree(comments)


@router.get("/{comment_id}", response_model=Comment)
async def read_comment(comment_id: int):
    """Get a comment by ID (public endpoint)."""
    db_comment = await get_comment(comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )
    return db_comment


@router.put("/{comment_id}", response_model=Comment)
async def update_existing_comment(
    comment_id: int,
    comment_data: CommentUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a comment. Only the owner can update."""
    db_comment = await update_comment(comment_id, current_user.id, comment_data)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Comment not found or you don't have permission to update it"
        )
    return db_comment


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
):
    """Delete a comment. Owner or staff can delete."""
    deleted = await delete_comment(comment_id, current_user.id, current_user.is_staff)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Comment not found or you don't have permission to delete it"
        )
    return None
