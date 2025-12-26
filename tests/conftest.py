"""Pytest configuration and fixtures for FastAPI + Tortoise ORM testing.

This module provides fixtures for testing FastAPI endpoints with Tortoise ORM.
It properly manages database connections to avoid asyncpg connection pool conflicts.
"""

import pytest
import os
import uuid
from typing import AsyncGenerator

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

# Set test environment BEFORE importing app
os.environ["PYTEST_CURRENT_TEST"] = "1"

from app.main import app
from app.models.user import User
from app.models.post import Post
from app.models.comment import Comment
from app.models.likes import Likes
from app.models.comment_likes import CommentLikes
from app.auth.jwt import create_access_token


# Database setup for tests - Use PostgreSQL test database
TEST_DB_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgres://postgres:password@localhost:5432/blog_post_test"
)
# Tortoise ORM requires 'postgres' not 'postgresql' in the URL
if TEST_DB_URL.startswith("postgresql://"):
    TEST_DB_URL = TEST_DB_URL.replace("postgresql://", "postgres://", 1)


@pytest.fixture(scope="session")
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"


@pytest.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client with proper lifespan management.

    Uses LifespanManager to properly handle FastAPI startup/shutdown events.
    This ensures database connections are properly initialized and closed.
    """
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test",
            timeout=30.0,
        ) as ac:
            yield ac


@pytest.fixture(scope="function")
async def test_user(client: AsyncClient) -> User:
    """Create a test user with unique identifier.

    Depends on client to ensure database is initialized.
    """
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"testuser_{unique_id}",
        email=f"test_{unique_id}@example.com",
        first_name="Test",
        last_name="User",
        is_active=True,
        is_staff=False,
    )
    user.set_password("TestPassword123!")
    await user.save()
    return user


@pytest.fixture(scope="function")
async def test_staff_user(client: AsyncClient) -> User:
    """Create a test staff user with unique identifier."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"staffuser_{unique_id}",
        email=f"staff_{unique_id}@example.com",
        first_name="Staff",
        last_name="User",
        is_active=True,
        is_staff=True,
    )
    user.set_password("StaffPassword123!")
    await user.save()
    return user


@pytest.fixture(scope="function")
async def test_superuser(client: AsyncClient) -> User:
    """Create a test superuser with unique identifier."""
    unique_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"superuser_{unique_id}",
        email=f"super_{unique_id}@example.com",
        first_name="Super",
        last_name="User",
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    user.set_password("SuperPassword123!")
    await user.save()
    return user


@pytest.fixture(scope="function")
async def test_user_token(test_user: User) -> str:
    """Generate JWT token for test user."""
    return create_access_token({"sub": test_user.username})


@pytest.fixture(scope="function")
async def test_staff_token(test_staff_user: User) -> str:
    """Generate JWT token for test staff user."""
    return create_access_token({"sub": test_staff_user.username})


@pytest.fixture(scope="function")
async def test_superuser_token(test_superuser: User) -> str:
    """Generate JWT token for test superuser."""
    return create_access_token({"sub": test_superuser.username})


@pytest.fixture(scope="function")
async def test_post(test_user: User) -> Post:
    """Create a test post."""
    post = Post(
        user=test_user,
        name="Test Post",
        title="Test Post Title",
        text="This is a test post content.",
        is_active=True,
    )
    await post.save()
    return post


@pytest.fixture(scope="function")
async def test_comment(test_user: User, test_post: Post) -> Comment:
    """Create a test comment."""
    comment = Comment(
        user=test_user,
        post=test_post,
        comment="This is a test comment.",
        is_active=True,
    )
    await comment.save()
    return comment


@pytest.fixture(scope="function")
async def test_like(test_user: User, test_post: Post) -> Likes:
    """Create a test like."""
    like = Likes(
        user=test_user,
        post=test_post,
        is_like=True,
    )
    await like.save()
    return like


@pytest.fixture(scope="function")
async def test_comment_like(test_user: User, test_comment: Comment) -> CommentLikes:
    """Create a test comment like."""
    comment_like = CommentLikes(
        user=test_user,
        comment=test_comment,
        is_like=True,
    )
    await comment_like.save()
    return comment_like
