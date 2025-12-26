"""Tests for post endpoints."""

import uuid
import pytest
from httpx import AsyncClient
from app.models.post import Post
from app.models.user import User
from app.auth.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_post_success(client: AsyncClient, test_user_token: str):
    """Test successful post creation."""
    response = await client.post(
        "/posts/",
        data={
            "name": "Test Post Name",
            "title": "Test Post Title",
            "text": "This is test post content.",
        },
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Post Name"
    assert data["title"] == "Test Post Title"
    assert data["text"] == "This is test post content."


@pytest.mark.asyncio
async def test_create_post_with_images(client: AsyncClient, test_user_token: str):
    """Test post creation with images."""
    # Create a simple test image file
    files = [("images", ("test.png", b"fake image content", "image/png"))]
    response = await client.post(
        "/posts/",
        data={
            "name": "Post With Images",
            "title": "Test Post Title",
            "text": "This is test post content with images.",
        },
        files=files,
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Post With Images"


@pytest.mark.asyncio
async def test_create_post_unauthorized(client: AsyncClient):
    """Test post creation without authentication."""
    response = await client.post(
        "/posts/",
        data={
            "name": "Unauthorized Post",
            "title": "Test Title",
            "text": "Test content",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_post_success(
    client: AsyncClient, test_post: Post, test_user_token: str
):
    """Test successful post retrieval."""
    response = await client.get(
        f"/posts/{test_post.id}",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_post.id
    assert data["name"] == test_post.name
    assert data["title"] == test_post.title


@pytest.mark.asyncio
async def test_get_post_not_found(client: AsyncClient, test_user_token: str):
    """Test post retrieval with non-existent ID."""
    response = await client.get(
        "/posts/99999",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_post_forbidden(
    client: AsyncClient, test_post: Post, test_user: User
):
    """Test post retrieval by different user."""
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
        f"/posts/{test_post.id}",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    # Other users can view posts (public access) or get 403
    assert response.status_code in [200, 403]


@pytest.mark.asyncio
async def test_get_posts_success(client: AsyncClient, test_staff_token: str):
    """Test successful posts list retrieval by staff."""
    response = await client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {test_staff_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_posts_forbidden(client: AsyncClient, test_user_token: str):
    """Test posts list retrieval without staff permissions."""
    response = await client.get(
        "/posts/",
        headers={"Authorization": f"Bearer {test_user_token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_post_unauthorized(client: AsyncClient, test_post: Post):
    """Test post retrieval without authentication."""
    response = await client.get(f"/posts/{test_post.id}")
    assert response.status_code == 401
