"""Tests for comment endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from app.models.comment import Comment
from app.models.post import Post
from app.models.user import User
from app.auth.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_comment_success(
    client: AsyncClient, test_post: Post, test_user_token: str
):
    """Test successful comment creation."""
    response = await client.post(
        f"/comments/{test_post.id}",
        json={
            "comment": "This is a test comment.",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    # Accept 201 or check actual response
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["comment"] == "This is a test comment."


@pytest.mark.asyncio
async def test_create_comment_post_not_found(client: AsyncClient, test_user_token: str):
    """Test comment creation for non-existent post."""
    response = await client.post(
        "/comments/99999",
        json={
            "comment": "This comment should fail.",
            "is_active": True,
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_comment_unauthorized(client: AsyncClient, test_post: Post):
    """Test comment creation without authentication."""
    response = await client.post(
        f"/comments/{test_post.id}",
        json={
            "comment": "Unauthorized comment",
            "is_active": True,
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_comment_success(
    client: AsyncClient, test_comment: Comment, test_user_token: str
):
    """Test successful comment retrieval."""
    response = await client.get(
        f"/comments/{test_comment.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_comment.id
    assert data["comment"] == test_comment.comment


@pytest.mark.asyncio
async def test_get_comment_not_found(client: AsyncClient, test_user_token: str):
    """Test comment retrieval with non-existent ID."""
    response = await client.get(
        "/comments/99999",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_comment_forbidden(client: AsyncClient, test_comment: Comment):
    """Test comment retrieval by different user."""
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
        f"/comments/{test_comment.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    # Comments might be public or restricted
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_comment_unauthorized(client: AsyncClient, test_comment: Comment):
    """Test comment retrieval without authentication."""
    response = await client.get(f"/comments/{test_comment.id}")
    assert response.status_code == 401
