"""User router endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from app.schemas.user import User, UserCreate
from app.crud.user import create_user, get_user, get_users
from app.auth.jwt import get_current_user
from app.models.user import User as UserModel
from app.core.exceptions import (
    NotFoundException,
    ForbiddenException,
    ValidationException,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_new_user(user: UserCreate):
    """Create a new user.

    Args:
        user: User creation data

    Returns:
        Created user object

    Raises:
        ValidationException: If user data is invalid
        ConflictException: If username or email already exists
    """
    try:
        return await create_user(user)
    except ValueError as e:
        raise ValidationException(str(e))


@router.get("/{user_id}", response_model=User)
async def read_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """Get a user by ID.

    Args:
        user_id: User ID
        current_user: Current authenticated user

    Returns:
        User object

    Raises:
        ForbiddenException: If user is not staff
        NotFoundException: If user not found
    """
    if not current_user.is_staff:
        raise ForbiddenException("Not enough permissions")

    db_user = await get_user(user_id)
    if db_user is None:
        raise NotFoundException("User", str(user_id))
    return db_user


@router.get("/", response_model=List[User])
async def read_users(current_user: UserModel = Depends(get_current_user)):
    """Get all users.

    Args:
        current_user: Current authenticated user

    Returns:
        List of users

    Raises:
        ForbiddenException: If user is not staff
    """
    if not current_user.is_staff:
        raise ForbiddenException("Not enough permissions")

    return await get_users()
