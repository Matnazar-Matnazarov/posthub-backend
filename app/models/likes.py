from tortoise.models import Model
from tortoise import fields
from app.config import settings
from datetime import datetime
from fastadmin import TortoiseModelAdmin, register
from uuid import UUID
from .user import User


class Likes(Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="likes")
    post = fields.ForeignKeyField("models.Post", related_name="likes")
    is_like = fields.BooleanField(default=True)
    created = fields.DatetimeField(
        auto_now_add=True, default=lambda: datetime.now(settings.TIMEZONE)
    )
    updated = fields.DatetimeField(
        auto_now=True, default=lambda: datetime.now(settings.TIMEZONE)
    )

    class Meta:
        table = "likes"
        indexes = [
            ("post_id",),
            ("is_like",),
            ("user_id", "post_id"),
        ]


@register(Likes)
class LikesAdmin(TortoiseModelAdmin):
    list_display = ("id", "user", "post", "is_like")
    list_display_links = ("id", "user", "post")
    list_filter = ("id", "user", "post", "is_like")
    search_fields = ("user", "post")

    async def get_user(self, user_id: int) -> UUID | int | None:
        user = await User.filter(id=user_id).first()
        if not user:
            print(f"Foydalanuvchi autopilot: {user_id}")
            return None
        return user.id
