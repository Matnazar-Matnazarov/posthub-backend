"""Post router endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, status, UploadFile, File, Form, Request
from fastapi.responses import FileResponse
from app.schemas.post import Post, PostCreate, PostImage, PostList, PostDetail, PostUpdate
from app.schemas.images import ImagesCreate
from app.crud.post import (
    create_post, 
    get_post_detail, 
    get_posts_public,
    get_user_posts,
    get_user_stats,
    update_post,
    delete_post
)
from app.websocket import notify_new_post
from app.auth.jwt import get_current_user
from app.models.user import User
from app.models.post import Post as PostModel
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


def get_client_ip(request: Request) -> str:
    """Get client IP address from request."""
    # Check for forwarded headers (behind proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


async def get_optional_user(request: Request) -> Optional[User]:
    """Get current user if authenticated, None otherwise."""
    try:
        from app.auth.jwt import get_token_from_request, decode_token, TokenType
        
        token = get_token_from_request(request)
        if not token:
            return None
        
        payload = decode_token(token, TokenType.ACCESS)
        username = payload.get("sub")
        if not username:
            return None
        
        user = await User.get_or_none(username=username)
        return user if user and user.is_active else None
    except Exception:
        return None


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_new_post(
    name: str = Form(...),
    title: str = Form(...),
    text: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    current_user: User = Depends(get_current_user),
):
    """Create a new post."""
    post = PostCreate(name=name, title=title, text=text)
    image_list = []
    if images:
        for image in images:
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
        new_post = await create_post(post, current_user.id, images=image_list)
        
        # Send notification to all users about new post
        author_name = f"{current_user.first_name} {current_user.last_name}".strip() or current_user.username
        await notify_new_post(new_post.id, title, author_name)
        
        return new_post
    except ValueError as e:
        raise ValidationException(str(e))


@router.get("/", response_model=List[PostList])
async def read_posts_public(
    skip: int = 0,
    limit: int = 20,
):
    """Get all public posts (no auth required)."""
    return await get_posts_public(skip, limit)


@router.get("/my", response_model=List[PostList])
async def read_my_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    """Get current user's posts."""
    return await get_user_posts(current_user.id, skip, limit)


@router.get("/stats")
async def get_my_stats(current_user: User = Depends(get_current_user)):
    """Get current user's post statistics for dashboard."""
    return await get_user_stats(current_user.id)


@router.get("/{post_id}", response_model=PostDetail)
async def read_post(
    post_id: int,
    request: Request,
):
    """Get a post by ID (public endpoint, records view)."""
    user = await get_optional_user(request)
    ip_address = get_client_ip(request)
    user_agent = request.headers.get("User-Agent")
    
    db_post = await get_post_detail(
        post_id, 
        user_id=user.id if user else None,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    if db_post is None:
        raise NotFoundException("Post", str(post_id))
    
    return db_post


@router.put("/{post_id}", response_model=PostImage)
async def update_existing_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update a post. Only owner or staff can update."""
    db_post = await update_post(post_id, current_user.id, post_data, current_user.is_staff)
    if db_post is None:
        raise NotFoundException("Post", str(post_id))
    return db_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
):
    """Delete a post. Only owner or staff can delete."""
    deleted = await delete_post(post_id, current_user.id, current_user.is_staff)
    if not deleted:
        raise NotFoundException("Post", str(post_id))
    return None


@router.get("/images/{image_path:path}", response_class=FileResponse)
async def get_image(image_path: str):
    """Get an image file."""
    file_path = Path(image_path)
    if not file_path.exists():
        raise NotFoundException("Image", image_path)
    return FileResponse(file_path)
