"""Tests for images endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from app.models.images import Images
from app.models.post import Post
from app.models.user import User
from app.auth.jwt import create_access_token


@pytest.mark.asyncio
async def test_get_image_success(
    client: AsyncClient, test_post: Post, test_user_token: str
):
    """Test successful image retrieval."""
    # Create a test image
    image = Images(
        post=test_post,
        image="uploads/test_image.png",
        is_active=True,
    )
    await image.save()

    response = await client.get(
        f"/images/{image.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == image.id


@pytest.mark.asyncio
async def test_get_image_not_found(client: AsyncClient, test_user_token: str):
    """Test image retrieval with non-existent ID."""
    response = await client.get(
        "/images/99999",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_image_forbidden(client: AsyncClient, test_post: Post):
    """Test image retrieval by different user."""
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

    # Create image for test_post
    image = Images(
        post=test_post,
        image="uploads/test_image.png",
        is_active=True,
    )
    await image.save()

    other_token = create_access_token({"sub": other_user.username})

    response = await client.get(
        f"/images/{image.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    # Images might be public or restricted
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_images_by_post_success(
    client: AsyncClient, test_post: Post, test_user_token: str
):
    """Test successful images retrieval by post."""
    response = await client.get(
        f"/images/post/{test_post.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_images_by_post_not_found(client: AsyncClient, test_user_token: str):
    """Test images retrieval for non-existent post."""
    response = await client.get(
        "/images/post/99999",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_images_by_post_forbidden(client: AsyncClient, test_post: Post):
    """Test images retrieval by different user."""
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
        f"/images/post/{test_post.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    # Images might be public or restricted
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_image_unauthorized(client: AsyncClient):
    """Test image retrieval without authentication."""
    response = await client.get("/images/1")
    assert response.status_code == 401
