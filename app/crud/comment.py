"""Comment CRUD operations."""

from typing import Optional, List
from app.models.comment import Comment
from app.models.comment_likes import CommentLikes
from app.schemas.comment import CommentCreate, CommentUpdate, CommentWithUser
from app.models.post import Post


async def create_comment(
    comment: CommentCreate, user_id: int, post_id: int
) -> Comment:
    """Create a new comment."""
    if not await Post.filter(id=post_id).exists():
        raise ValueError("Post not found")
    
    # Verify parent comment exists if provided
    if comment.parent_id:
        parent = await Comment.get_or_none(id=comment.parent_id, post_id=post_id)
        if not parent:
            raise ValueError("Parent comment not found")

    db_comment = Comment(
        comment=comment.comment,
        is_active=comment.is_active,
        user_id=user_id,
        post_id=post_id,
        parent_id=comment.parent_id
    )
    await db_comment.save()
    return db_comment


async def get_comment(comment_id: int) -> Optional[Comment]:
    """Get a comment by ID."""
    return await Comment.get_or_none(id=comment_id).prefetch_related("comment_likes", "user")


async def update_comment(
    comment_id: int, user_id: int, update_data: CommentUpdate
) -> Optional[Comment]:
    """Update a comment. Only owner can update."""
    comment = await Comment.get_or_none(id=comment_id, user_id=user_id)
    if not comment:
        return None
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(comment, key, value)
    
    await comment.save()
    return comment


async def delete_comment(comment_id: int, user_id: int, is_staff: bool = False) -> bool:
    """Delete a comment. Owner or staff can delete."""
    if is_staff:
        comment = await Comment.get_or_none(id=comment_id)
    else:
        comment = await Comment.get_or_none(id=comment_id, user_id=user_id)
    
    if not comment:
        return False
    
    # Delete all replies first
    await Comment.filter(parent_id=comment_id).delete()
    await comment.delete()
    return True


async def get_post_comments(post_id: int) -> List[Comment]:
    """Get all comments for a post (top-level only, with replies)."""
    comments = await Comment.filter(
        post_id=post_id, 
        is_active=True,
        parent_id=None  # Only top-level comments
    ).prefetch_related("user", "replies", "replies__user", "comment_likes").order_by("-created")
    
    return comments


async def build_comment_tree(comments: List[Comment]) -> List[CommentWithUser]:
    """Build comment tree with replies and likes count."""
    result = []
    
    for comment in comments:
        likes_count = await CommentLikes.filter(comment_id=comment.id, is_like=True).count()
        
        # Get replies
        replies = await Comment.filter(
            parent_id=comment.id, 
            is_active=True
        ).prefetch_related("user", "comment_likes").order_by("created")
        
        reply_list = []
        for reply in replies:
            reply_likes = await CommentLikes.filter(comment_id=reply.id, is_like=True).count()
            reply_list.append(CommentWithUser(
                id=reply.id,
                comment=reply.comment,
                is_active=reply.is_active,
                user_id=reply.user_id,
                post_id=reply.post_id,
                parent_id=reply.parent_id,
                created=reply.created,
                updated=reply.updated,
                user={
                    "id": reply.user.id,
                    "username": reply.user.username,
                    "first_name": reply.user.first_name,
                    "last_name": reply.user.last_name,
                    "picture": reply.user.picture,
                } if reply.user else None,
                replies=[],
                likes_count=reply_likes
            ))
        
        result.append(CommentWithUser(
            id=comment.id,
            comment=comment.comment,
            is_active=comment.is_active,
            user_id=comment.user_id,
            post_id=comment.post_id,
            parent_id=comment.parent_id,
            created=comment.created,
            updated=comment.updated,
            user={
                "id": comment.user.id,
                "username": comment.user.username,
                "first_name": comment.user.first_name,
                "last_name": comment.user.last_name,
                "picture": comment.user.picture,
            } if comment.user else None,
            replies=reply_list,
            likes_count=likes_count
        ))
    
    return result
