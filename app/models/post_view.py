"""Post view tracking model."""

from tortoise.models import Model
from tortoise import fields
from datetime import datetime
from app.config import settings
from fastadmin import TortoiseModelAdmin, register


class PostView(Model):
    """Track post views by IP address or user."""
    
    id = fields.BigIntField(primary_key=True)
    post = fields.ForeignKeyField("models.Post", related_name="views")
    user = fields.ForeignKeyField("models.User", related_name="post_views", null=True)
    ip_address = fields.CharField(max_length=45)  # IPv6 compatible
    user_agent = fields.CharField(max_length=500, null=True)
    created = fields.DatetimeField(
        auto_now_add=True, default=lambda: datetime.now(settings.TIMEZONE)
    )

    class Meta:
        table = "post_view"
        indexes = [
            ("post_id",),
            ("ip_address",),
            ("user_id",),
            ("post_id", "ip_address"),
            ("post_id", "user_id"),
        ]


@register(PostView)
class PostViewAdmin(TortoiseModelAdmin):
    list_display = ("id", "post", "user", "ip_address", "created")
    list_display_links = ("id",)
    list_filter = ("post", "user")
    search_fields = ("ip_address",)

