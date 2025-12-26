from tortoise.models import Model
from tortoise import fields
from datetime import datetime
from app.config import settings
from fastadmin import TortoiseModelAdmin, register
from uuid import UUID
from .user import User


class Comment(Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="comments")
    post = fields.ForeignKeyField("models.Post", related_name="comments")
    comment = fields.TextField()
    is_active = fields.BooleanField(default=True)
    created = fields.DatetimeField(
        auto_now_add=True, default=lambda: datetime.now(settings.TIMEZONE)
    )
    updated = fields.DatetimeField(
        auto_now=True, default=lambda: datetime.now(settings.TIMEZONE)
    )

    comment_likes = fields.ReverseRelation["CommentLikes"]

    class Meta:
        table = "comment"
        indexes = [
            ("post_id",),
            ("is_active",),
            ("user_id", "post_id", "is_active", "created"),
        ]


@register(Comment)
class CommentAdmin(TortoiseModelAdmin):
    list_display = ("id", "user", "post", "is_active")
    list_display_links = ("id", "user", "post")
    list_filter = ("id", "user", "post", "is_active")
    search_fields = ("user", "post")

    async def get_user(self, user_id: int) -> UUID | int | None:
        user = await User.filter(id=user_id).first()
        if not user:
            print(f"Foydalanuvchi autopilot: {user_id}")
            return None
        return user.id
