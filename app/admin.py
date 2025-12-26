"""FastAdmin configuration for admin panel.

This module configures the FastAdmin admin panel for managing
database models through a web interface.

Note: Environment variables MUST be set before importing fastadmin,
which causes E402 linting warnings that are intentionally suppressed.
"""

import os
from typing import Optional
from uuid import UUID

# Configure FastAdmin environment BEFORE importing
# ADMIN_USER_MODEL should be the ORM model class name (User)
from app.config import settings as app_settings  # noqa: E402

os.environ["ADMIN_USER_MODEL"] = "User"
os.environ["ADMIN_USER_MODEL_USERNAME_FIELD"] = "username"
os.environ["ADMIN_SECRET_KEY"] = app_settings.JWT_SECRET_KEY

from fastadmin import TortoiseModelAdmin, register  # noqa: E402
from fastadmin.settings import settings as fastadmin_settings  # noqa: E402

# Force update FastAdmin settings at runtime
fastadmin_settings.ADMIN_USER_MODEL = "User"
fastadmin_settings.ADMIN_USER_MODEL_USERNAME_FIELD = "username"
fastadmin_settings.ADMIN_SECRET_KEY = app_settings.JWT_SECRET_KEY

from app.models.user import User  # noqa: E402
from app.models.post import Post  # noqa: E402
from app.models.comment import Comment  # noqa: E402
from app.models.likes import Likes  # noqa: E402
from app.models.comment_likes import CommentLikes  # noqa: E402
from app.models.images import Images  # noqa: E402


@register(User)
class UserAdmin(TortoiseModelAdmin):
    """Admin configuration for User model.

    Provides user management with authentication support for admin access.
    Only superusers can log into the admin panel.
    """

    exclude = ("password",)
    list_display = (
        "id",
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
        "created",
    )
    list_display_links = ("id", "username")
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-created",)

    async def authenticate(self, username: str, password: str) -> Optional[UUID | int]:
        """Authenticate admin user for panel access.

        Args:
            username: Admin username
            password: Admin password

        Returns:
            User ID if authenticated successfully, None otherwise
        """
        user = await User.filter(username=username).first()

        if not user:
            return None

        if not user.check_password(password):
            return None

        if not user.is_superuser:
            return None

        if not user.is_active:
            return None

        return user.id


@register(Post)
class PostAdmin(TortoiseModelAdmin):
    """Admin configuration for Post model."""

    list_display = ("id", "name", "title", "user_id", "is_active", "created")
    list_display_links = ("id", "name", "title")
    list_filter = ("is_active",)
    search_fields = ("name", "title", "text")
    ordering = ("-created",)


@register(Comment)
class CommentAdmin(TortoiseModelAdmin):
    """Admin configuration for Comment model."""

    list_display = ("id", "comment", "user_id", "post_id", "is_active", "created")
    list_display_links = ("id",)
    list_filter = ("is_active",)
    search_fields = ("comment",)
    ordering = ("-created",)


@register(Likes)
class LikesAdmin(TortoiseModelAdmin):
    """Admin configuration for Likes model."""

    list_display = ("id", "user_id", "post_id", "is_like", "created")
    list_display_links = ("id",)
    list_filter = ("is_like",)
    ordering = ("-created",)


@register(CommentLikes)
class CommentLikesAdmin(TortoiseModelAdmin):
    """Admin configuration for CommentLikes model."""

    list_display = ("id", "user_id", "comment_id", "is_like", "created")
    list_display_links = ("id",)
    list_filter = ("is_like",)
    ordering = ("-created",)


@register(Images)
class ImagesAdmin(TortoiseModelAdmin):
    """Admin configuration for Images model."""

    list_display = ("id", "image", "post_id", "is_active", "created")
    list_display_links = ("id",)
    list_filter = ("is_active",)
    ordering = ("-created",)
