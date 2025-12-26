from tortoise.models import Model
from tortoise import fields
from app.config import settings
from datetime import datetime
from fastadmin import TortoiseModelAdmin, register
from uuid import UUID
from .user import User


class Post(Model):
    id = fields.BigIntField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="posts")
    name = fields.CharField(max_length=255)
    title = fields.CharField(max_length=255)
    text = fields.TextField()
    is_active = fields.BooleanField(default=True)
    created = fields.DatetimeField(
        auto_now_add=True, default=lambda: datetime.now(settings.TIMEZONE)
    )
    updated = fields.DatetimeField(
        auto_now=True, default=lambda: datetime.now(settings.TIMEZONE)
    )

    images = fields.ReverseRelation["Images"]
    comments = fields.ReverseRelation["Comment"]
    likes = fields.ReverseRelation["Likes"]

    class Meta:
        table = "post"
        indexes = [
            ("is_active",),
            ("user_id", "created", "is_active"),
        ]


@register(Post)
class PostAdmin(TortoiseModelAdmin):
    list_display = ("id", "name", "title", "is_active")
    list_display_links = ("id", "name")
    list_filter = ("id", "name", "title", "is_active")
    search_fields = ("name", "title")

    async def get_user(self, user_id: int) -> UUID | int | None:
        user = await User.filter(id=user_id).first()
        if not user:
            print(f"Foydalanuvchi autopilot: {user_id}")
            return None
        return user.id
