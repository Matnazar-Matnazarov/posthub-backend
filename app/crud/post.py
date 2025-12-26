"""Post CRUD operations with optimized queries."""

from typing import List, Optional
from app.models.post import Post
from app.schemas.post import PostCreate, PostImage
from app.crud.images import create_image


async def create_post(
    post: PostCreate, user_id: int, images: Optional[List] = None
) -> Post:
    """Create a new post with optional images.

    Args:
        post: Post creation data
        user_id: Author user ID
        images: Optional list of image files

    Returns:
        Created post
    """
    db_post = Post(**post.model_dump(), user_id=user_id)
    await db_post.save()

    if images:
        for image in images:
            await create_image(image, db_post.id)

    # Return with images prefetched
    return await Post.get(id=db_post.id).prefetch_related("images")


async def get_post(post_id: int, include_relations: bool = False) -> Optional[Post]:
    """Get post by ID.

    Args:
        post_id: Post ID
        include_relations: Whether to include images, comments, likes

    Returns:
        Post or None
    """
    query = Post.filter(id=post_id)

    if include_relations:
        query = query.prefetch_related("images", "comments", "likes")

    return await query.first()


async def get_post_with_details(post_id: int) -> Optional[PostImage]:
    """Get post with all details for response.

    Args:
        post_id: Post ID

    Returns:
        PostImage schema or None
    """
    post = await Post.get_or_none(id=post_id).prefetch_related("images")

    if post:
        return PostImage.model_validate(post)
    return None


async def get_posts(
    skip: int = 0,
    limit: int = 20,
    user_id: Optional[int] = None,
    is_active: bool = True,
) -> List[PostImage]:
    """Get posts with pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        user_id: Filter by user ID
        is_active: Filter by active status

    Returns:
        List of posts with images
    """
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
    """Get posts count.

    Args:
        user_id: Filter by user ID
        is_active: Filter by active status

    Returns:
        Total count
    """
    query = Post.filter(is_active=is_active)

    if user_id:
        query = query.filter(user_id=user_id)

    return await query.count()


async def get_user_posts(user_id: int, skip: int = 0, limit: int = 20) -> List[Post]:
    """Get posts by user ID.

    Args:
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records

    Returns:
        List of posts
    """
    return (
        await Post.filter(user_id=user_id, is_active=True)
        .prefetch_related("images")
        .offset(skip)
        .limit(limit)
        .order_by("-created")
    )


async def update_post(
    post_id: int, post_data: PostCreate, images: Optional[List] = None
) -> Optional[Post]:
    """Update post.

    Args:
        post_id: Post ID
        post_data: Updated post data
        images: Optional new images

    Returns:
        Updated post or None
    """
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        return None

    for key, value in post_data.model_dump(exclude_unset=True).items():
        setattr(db_post, key, value)
    await db_post.save()

    # Update images if provided
    if images is not None:
        # Delete existing images
        await db_post.images.all().delete()
        # Add new images
        for image in images:
            await create_image(image, db_post.id)

    return await Post.get(id=post_id).prefetch_related("images")


async def delete_post(post_id: int) -> bool:
    """Delete post by ID.

    Args:
        post_id: Post ID

    Returns:
        True if deleted, False if not found
    """
    db_post = await Post.get_or_none(id=post_id)
    if not db_post:
        return False

    await db_post.delete()
    return True
