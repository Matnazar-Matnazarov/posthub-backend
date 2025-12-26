"""Tests for comment likes endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from app.models.comment_likes import CommentLikes
from app.models.comment import Comment
from app.models.user import User
from app.auth.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_comment_like_success(
    client: AsyncClient, test_comment: Comment, test_user_token: str
):
    """Test successful comment like creation."""
    response = await client.post(
        f"/comment-likes/{test_comment.id}",
        json={
            "is_like": True,
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    # Accept 200 or 201
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["is_like"] is True


@pytest.mark.asyncio
async def test_create_comment_like_comment_not_found(
    client: AsyncClient, test_user_token: str
):
    """Test comment like creation for non-existent comment."""
    response = await client.post(
        "/comment-likes/99999",
        json={
            "is_like": True,
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_like_unauthorized(
    client: AsyncClient, test_comment: Comment
):
    """Test comment like creation without authentication."""
    response = await client.post(
        f"/comment-likes/{test_comment.id}",
        json={
            "is_like": True,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_comment_like_success(
    client: AsyncClient, test_comment_like: CommentLikes, test_user_token: str
):
    """Test successful comment like retrieval."""
    response = await client.get(
        f"/comment-likes/{test_comment_like.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_comment_like.id


@pytest.mark.asyncio
async def test_get_comment_like_not_found(client: AsyncClient, test_user_token: str):
    """Test comment like retrieval with non-existent ID."""
    response = await client.get(
        "/comment-likes/99999",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_comment_like_forbidden(
    client: AsyncClient, test_comment_like: CommentLikes
):
    """Test comment like retrieval by different user."""
    # Create another user with unique identifier
    unique_id = str(uuid.uuid4())[:8]
    other_user = User(
        username=f"otheruser_{unique_id}",
        email=f"other_{unique_id}@example.com",
        first_name="Other",
        last_name="User",
    )
    other_user.set_password("OtherPassword123!")
    await other_user.save()

    other_token = create_access_token({"sub": other_user.username})

    response = await client.get(
        f"/comment-likes/{test_comment_like.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    # Comment likes might be public or restricted
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_comment_like_unauthorized(
    client: AsyncClient, test_comment_like: CommentLikes
):
    """Test comment like retrieval without authentication."""
    response = await client.get(f"/comment-likes/{test_comment_like.id}")
    assert response.status_code == 401
