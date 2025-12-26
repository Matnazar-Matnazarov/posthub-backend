"""User model for authentication and authorization."""

from tortoise.models import Model
from tortoise import fields
from passlib.hash import bcrypt


class User(Model):
    """User model for authentication and authorization.

    Attributes:
        id: Primary key
        username: Unique username
        password: Hashed password
        first_name: User's first name
        last_name: User's last name
        email: Unique email address
        is_active: Whether user account is active
        is_staff: Whether user has staff privileges
        is_superuser: Whether user has superuser privileges
        picture: Optional profile picture URL
        phone: Optional phone number
        created: Creation timestamp
        updated: Last update timestamp
    """

    id = fields.BigIntField(primary_key=True)
    username = fields.CharField(max_length=255, unique=True, db_index=True)
    password = fields.CharField(max_length=128)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255, unique=True, db_index=True)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    picture = fields.CharField(max_length=255, null=True)
    phone = fields.CharField(max_length=20, null=True)
    created = fields.DatetimeField(auto_now_add=True)
    updated = fields.DatetimeField(auto_now=True)

    # Relationships
    posts: fields.ReverseRelation["Post"]  # noqa: F821
    comments: fields.ReverseRelation["Comment"]  # noqa: F821
    likes: fields.ReverseRelation["Likes"]  # noqa: F821
    comment_likes: fields.ReverseRelation["CommentLikes"]  # noqa: F821

    class Meta:
        table = "users"
        ordering = ["-created"]

    def __str__(self) -> str:
        return f"{self.username} ({self.email})"

    def set_password(self, raw_password: str) -> None:
        """Hash and set the user's password.

        Args:
            raw_password: Plain text password
        """
        self.password = bcrypt.hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify a password against the stored hash.

        Args:
            raw_password: Plain text password to check

        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.verify(raw_password, self.password)
        except Exception:
            return False

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def is_admin(self) -> bool:
        """Check if user is admin (staff or superuser)."""
        return self.is_staff or self.is_superuser
