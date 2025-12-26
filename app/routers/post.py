"""Post router endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, Form
from fastapi.responses import FileResponse
from app.schemas.post import Post, PostCreate, PostImage
from app.schemas.images import ImagesCreate
from app.crud.post import create_post, get_post_with_details, get_posts
from app.auth.jwt import get_current_user
from app.models.user import User
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
)
from app.config import settings
from pathlib import Path
from starlette.formparsers import MultiPartParser
import uuid
import logging

logger = logging.getLogger(__name__)

MultiPartParser.max_part_size = settings.MAX_UPLOAD_SIZE

router = APIRouter(prefix="/posts", tags=["posts"])

UPLOAD_DIR = settings.UPLOAD_DIR
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    name: str = Form(...),
    title: str = Form(...),
    text: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
):
    """Create a new post.

    Args:
        name: Post name
        title: Post title
        text: Post text content
        images: Optional list of image files
        current_user: Current authenticated user

    Returns:
        Created post object

    Raises:
        ValidationException: If post data is invalid
    """
    post = PostCreate(name=name, title=title, text=text)
    image_list = []
    if images:
        for image in images:
            # Validate file extension
            file_ext = Path(image.filename).suffix.lower()
            if file_ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
                raise ValidationException(
                    f"File extension {file_ext} not allowed. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
                )

            file_path = UPLOAD_DIR / f"{uuid.uuid4()}{file_ext}"
            try:
                with file_path.open("wb") as buffer:
                    content = await image.read()
                    if len(content) > settings.MAX_UPLOAD_SIZE:
                        raise ValidationException(
                            f"File size exceeds {settings.MAX_UPLOAD_SIZE} bytes"
                        )
                    buffer.write(content)
                image_list.append(ImagesCreate(image=str(file_path), is_active=True))
            except Exception as e:
                logger.error(f"Error saving image: {e}")
                raise ValidationException("Error saving image file")

    try:
        return await create_post(post, current_user.id, images=image_list)
    except ValueError as e:
        raise ValidationException(str(e))


@router.get("/{post_id}", response_model=PostImage)
async def read_post(post_id: int, current_user: User = Depends(get_current_user)):
    """Get a post by ID.

    Args:
        post_id: Post ID
        current_user: Current authenticated user

    Returns:
        Post object with images

    Raises:
        NotFoundException: If post not found
        ForbiddenException: If user doesn't have permission to view this post
    """
    db_post = await get_post_with_details(post_id)
    if db_post is None:
        raise NotFoundException("Post", str(post_id))
    if db_post.user_id != current_user.id and not current_user.is_staff:
        raise ForbiddenException("Not enough permissions to view this post")
    return db_post


@router.get("/", response_model=List[PostImage])
async def read_posts(current_user: User = Depends(get_current_user)):
    """Get all posts.

    Args:
        current_user: Current authenticated user

    Returns:
        List of posts with images

    Raises:
        ForbiddenException: If user is not staff
    """
    if not current_user.is_staff:
        raise ForbiddenException("Not enough permissions to view all posts")
    return await get_posts()


@router.get("/images/{image_path:path}", response_class=FileResponse)
async def get_image(image_path: str):
    """Get an image file.

    Args:
        image_path: Path to the image file

    Returns:
        Image file response

    Raises:
        NotFoundException: If image file not found
    """
    file_path = Path(image_path)
    if not file_path.exists():
        raise NotFoundException("Image", image_path)
    return FileResponse(file_path)
