"""User CRUD operations with optimized queries."""

from typing import List, Optional
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.exceptions import ConflictException


async def create_user(user: UserCreate) -> User:
    """Create a new user.

    Args:
        user: User creation data

    Returns:
        Created user object

    Raises:
        ConflictException: If username or email already exists
    """
    # Use single query with OR condition for efficiency
    existing = await User.filter(username=user.username).first()
    if existing:
        raise ConflictException("Username already exists")

    existing = await User.filter(email=user.email).first()
    if existing:
        raise ConflictException("Email already exists")

    db_user = User(
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        picture=user.picture,
        phone=user.phone,
        is_active=user.is_active,
        is_staff=user.is_staff,
    )
    db_user.set_password(user.password)
    await db_user.save()
    return db_user


async def get_user(user_id: int) -> Optional[User]:
    """Get user by ID.

    Args:
        user_id: User ID

    Returns:
        User or None
    """
    return await User.get_or_none(id=user_id)


async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username.

    Args:
        username: Username

    Returns:
        User or None
    """
    return await User.get_or_none(username=username)


async def get_user_by_email(email: str) -> Optional[User]:
    """Get user by email.

    Args:
        email: Email address

    Returns:
        User or None
    """
    return await User.get_or_none(email=email)


async def get_users(
    skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[User]:
    """Get users with pagination and filtering.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_active: Filter by active status

    Returns:
        List of users
    """
    query = User.all()

    if is_active is not None:
        query = query.filter(is_active=is_active)

    return await query.offset(skip).limit(limit).order_by("-created")


async def get_users_count(is_active: Optional[bool] = None) -> int:
    """Get total users count.

    Args:
        is_active: Filter by active status

    Returns:
        Total count
    """
    query = User.all()

    if is_active is not None:
        query = query.filter(is_active=is_active)

    return await query.count()


async def update_user(user_id: int, **kwargs) -> Optional[User]:
    """Update user fields.

    Args:
        user_id: User ID
        **kwargs: Fields to update

    Returns:
        Updated user or None
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        return None

    # Handle password separately
    password = kwargs.pop("password", None)
    if password:
        user.set_password(password)

    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)

    await user.save()
    return user


async def delete_user(user_id: int) -> bool:
    """Delete user by ID.

    Args:
        user_id: User ID

    Returns:
        True if deleted, False if not found
    """
    user = await User.get_or_none(id=user_id)
    if not user:
        return False

    await user.delete()
    return True
