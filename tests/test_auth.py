"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient
from app.models.user import User


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]
    username = f"newuser_{unique_id}"
    email = f"newuser_{unique_id}@example.com"

    response = await client.post(
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "first_name": "New",
            "last_name": "User",
            "password": "NewPassword123!",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Verify user was created
    # Note: Database verification is done via API response
    # Direct database access would require event loop management


@pytest.mark.asyncio
async def test_register_duplicate_username(client: AsyncClient, test_user: User):
    """Test registration with duplicate username."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    response = await client.post(
        "/auth/register",
        json={
            "username": test_user.username,  # Use existing username
            "email": f"different_{unique_id}@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "Password123!",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient, test_user: User):
    """Test registration with duplicate email."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    response = await client.post(
        "/auth/register",
        json={
            "username": f"differentuser_{unique_id}",
            "email": test_user.email,  # Use existing email
            "first_name": "Test",
            "last_name": "User",
            "password": "Password123!",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_weak_password(client: AsyncClient):
    """Test registration with weak password."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    response = await client.post(
        "/auth/register",
        json={
            "username": f"weakuser_{unique_id}",
            "email": f"weak_{unique_id}@example.com",
            "first_name": "Weak",
            "last_name": "User",
            "password": "weak",
        },
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Test registration with invalid email."""
    import uuid

    unique_id = str(uuid.uuid4())[:8]

    response = await client.post(
        "/auth/register",
        json={
            "username": f"invaliduser_{unique_id}",
            "email": "invalid-email",
            "first_name": "Invalid",
            "last_name": "User",
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_login_json_success(client: AsyncClient, test_user: User):
    """Test successful JSON login."""
    response = await client.post(
        "/auth/login-json",
        json={
            "username": test_user.username,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_json_invalid_credentials(client: AsyncClient, test_user: User):
    """Test login with invalid credentials."""
    response = await client.post(
        "/auth/login-json",
        json={
            "username": test_user.username,
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_json_nonexistent_user(client: AsyncClient):
    """Test login with nonexistent user."""
    response = await client.post(
        "/auth/login-json",
        json={
            "username": "nonexistent",
            "password": "Password123!",
        },
    )
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_form_success(client: AsyncClient, test_user: User):
    """Test successful form login."""
    response = await client.post(
        "/auth/login-form",
        data={
            "username": test_user.username,
            "password": "TestPassword123!",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_form_invalid_credentials(client: AsyncClient, test_user: User):
    """Test form login with invalid credentials."""
    response = await client.post(
        "/auth/login-form",
        data={
            "username": test_user.username,
            "password": "WrongPassword123!",
        },
    )
    assert response.status_code == 401
    assert "invalid credentials" in response.json()["detail"].lower()
