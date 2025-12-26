"""Post CRUD operations with optimized queries."""

from typing import List, Optional
from app.models.post import Post
from app.models.likes import Likes
from app.models.comment import Comment
from app.models.post_view import PostView
from app.schemas.post import PostCreate, PostImage, PostList, PostDetail, PostUpdate
from app.schemas.likes import LikesStats
from app.crud.images import create_image
from app.crud.comment import get_post_comments, build_comment_tree
from app.crud.likes import get_likes_stats


async def create_post(
    post: PostCreate, user_id: int, images: Optional[List] = None
) -> Post:
    """Create a new post with optional images."""
    db_post = Post(**post.model_dump(), user_id=user_id)
    await db_post.save()

    if images:
        for image in images:
            await create_image(image, db_post.id)

    return await Post.get(id=db_post.id).prefetch_related("images")


async def get_post(post_id: int, include_relations: bool = False) -> Optional[Post]:
    """Get post by ID."""
    query = Post.filter(id=post_id)

    if include_relations:
        query = query.prefetch_related("images", "comments", "likes")

    return await query.first()


async def get_post_with_details(post_id: int) -> Optional[PostImage]:
    """Get post with images."""
    post = await Post.get_or_none(id=post_id).prefetch_related("images")

    if post:
        return PostImage.model_validate(post)
    return None


async def get_post_detail(
    post_id: int, 
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[PostDetail]:
    """Get full post detail with comments, likes, views."""
    post = await Post.get_or_none(id=post_id, is_active=True).prefetch_related("images", "user")
    
    if not post:
        return None
    
    # Record view
    if ip_address:
        from app.crud.post_view import record_view
        await record_view(post_id, ip_address, user_id, user_agent)
    
    # Get stats
    likes_count = await Likes.filter(post_id=post_id, is_like=True).count()
    dislikes_count = await Likes.filter(post_id=post_id, is_like=False).count()
    comments_count = await Comment.filter(post_id=post_id, is_active=True).count()
    views_count = await PostView.filter(post_id=post_id).count()
    
    # Get user's like status
    user_liked = None
    if user_id:
        user_like = await Likes.get_or_none(user_id=user_id, post_id=post_id)
        if user_like:
            user_liked = user_like.is_like
    
    # Get comments with replies
    comments = await get_post_comments(post_id)
    comment_tree = await build_comment_tree(comments)
    
    return PostDetail(
        id=post.id,
        name=post.name,
        title=post.title,
        text=post.text,
        user_id=post.user_id,
        user={
            "id": post.user.id,
            "username": post.user.username,
            "first_name": post.user.first_name,
            "last_name": post.user.last_name,
            "picture": post.user.picture,
        } if post.user else None,
        created=post.created,
        updated=post.updated,
        images=[{"id": img.id, "image": img.image, "is_active": img.is_active, "post_id": img.post_id, "created": img.created} for img in post.images],
        likes_count=likes_count,
        dislikes_count=dislikes_count,
        comments_count=comments_count,
        views_count=views_count,
        comments=comment_tree,
        likes=LikesStats(
            likes_count=likes_count,
            dislikes_count=dislikes_count,
            user_liked=user_liked
        ),
        user_liked=user_liked,
        is_owner=user_id == post.user_id if user_id else False
    )


async def get_posts_public(
    skip: int = 0,
    limit: int = 20,
) -> List[PostList]:
    """Get public posts list with stats."""
    posts = await Post.filter(is_active=True).prefetch_related("images", "user").offset(skip).limit(limit).order_by("-created")
    
    result = []
    for post in posts:
        likes_count = await Likes.filter(post_id=post.id, is_like=True).count()
        dislikes_count = await Likes.filter(post_id=post.id, is_like=False).count()
        comments_count = await Comment.filter(post_id=post.id, is_active=True).count()
        views_count = await PostView.filter(post_id=post.id).count()
        
        result.append(PostList(
            id=post.id,
            name=post.name,
            title=post.title,
            text=post.text,
            user_id=post.user_id,
            user={
                "id": post.user.id,
                "username": post.user.username,
                "first_name": post.user.first_name,
                "last_name": post.user.last_name,
                "picture": post.user.picture,
            } if post.user else None,
            created=post.created,
            updated=post.updated,
            images=[{"id": img.id, "image": img.image, "is_active": img.is_active, "post_id": img.post_id, "created": img.created} for img in post.images],
            likes_count=likes_count,
            dislikes_count=dislikes_count,
            comments_count=comments_count,
            views_count=views_count
        ))
    
    return result


async def get_posts(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    is_active: bool = True,
) -> List[PostImage]:
    """Get posts with pagination and filtering."""
    query = Post.filter(is_active=is_active)

    if user_id:
        query = query.filter(user_id=user_id)

    posts = (
        await query.prefetch_related("images")
        .offset(skip)
        .limit(limit)
        .order_by("-created")
    )

    return [PostImage.model_validate(post) for post in posts]


async def get_posts_count(user_id: Optional[int] = None, is_active: bool = True) -> int:
    """Get posts count."""
    query = Post.filter(is_active=is_active)

    if user_id:
        query = query.filter(user_id=user_id)

    return await query.count()


async def get_user_posts(user_id: int, skip: int = 0, limit: int = 20) -> List[PostList]:
    """Get posts by user ID with stats."""
    posts = await Post.filter(user_id=user_id, is_active=True).prefetch_related("images", "user").offset(skip).limit(limit).order_by("-created")
    
    result = []
    for post in posts:
        likes_count = await Likes.filter(post_id=post.id, is_like=True).count()
        dislikes_count = await Likes.filter(post_id=post.id, is_like=False).count()
        comments_count = await Comment.filter(post_id=post.id, is_active=True).count()
        views_count = await PostView.filter(post_id=post.id).count()
        
        result.append(PostList(
            id=post.id,
            name=post.name,
            title=post.title,
            text=post.text,
            user_id=post.user_id,
            user={
                "id": post.user.id,
                "username": post.user.username,
                "first_name": post.user.first_name,
                "last_name": post.user.last_name,
                "picture": post.user.picture,
            } if post.user else None,
            created=post.created,
            updated=post.updated,
            images=[{"id": img.id, "image": img.image, "is_active": img.is_active, "post_id": img.post_id, "created": img.created} for img in post.images],
            likes_count=likes_count,
            dislikes_count=dislikes_count,
            comments_count=comments_count,
            views_count=views_count
        ))
    
    return result


async def update_post(
    post_id: int, user_id: int, post_data: PostUpdate, is_staff: bool = False
) -> Optional[Post]:
    """Update post. Only owner or staff can update."""
    if is_staff:
        db_post = await Post.get_or_none(id=post_id)
    else:
        db_post = await Post.get_or_none(id=post_id, user_id=user_id)
    
    if not db_post:
        return None

    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)
    await db_post.save()

    return await Post.get(id=post_id).prefetch_related("images")


async def delete_post(post_id: int, user_id: int, is_staff: bool = False) -> bool:
    """Delete post. Only owner or staff can delete."""
    if is_staff:
        db_post = await Post.get_or_none(id=post_id)
    else:
        db_post = await Post.get_or_none(id=post_id, user_id=user_id)
    
    if not db_post:
        return False

    await db_post.delete()
    return True


async def get_user_stats(user_id: int) -> dict:
    """Get user's post statistics."""
    posts_count = await Post.filter(user_id=user_id, is_active=True).count()
    total_likes = await Likes.filter(post__user_id=user_id, is_like=True).count()
    total_comments = await Comment.filter(post__user_id=user_id, is_active=True).count()
    total_views = await PostView.filter(post__user_id=user_id).count()
    
    return {
        "posts_count": posts_count,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views
    }
