from tortoise.models import Model
from tortoise import fields
from app.config import settings
from datetime import datetime
from fastadmin import TortoiseModelAdmin, register
from uuid import UUID
from .post import Post


class Images(Model):
    id = fields.BigIntField(primary_key=True)
    image = fields.CharField(max_length=255)
    post = fields.ForeignKeyField("models.Post", related_name="images")
    is_active = fields.BooleanField(default=True)
    created = fields.DatetimeField(
        auto_now_add=True, default=lambda: datetime.now(settings.TIMEZONE)
    )
    updated = fields.DatetimeField(
        auto_now=True, default=lambda: datetime.now(settings.TIMEZONE)
    )

    class Meta:
        table = "images"
        indexes = [
            ("post_id",),
            ("is_active",),
            ("post_id", "is_active"),
        ]


@register(Images)
class ImagesAdmin(TortoiseModelAdmin):
    list_display = ("id", "image", "post", "is_active")
    list_display_links = ("id", "image", "post")
    list_filter = ("id", "image", "post", "is_active")
    search_fields = ("image", "post")

    async def get_post(self, post_id: int) -> UUID | int | None:
        post = await Post.filter(id=post_id).first()
        if not post:
            print(f"Post autopilot: {post_id}")
            return None
