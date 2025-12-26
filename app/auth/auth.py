"""Authentication endpoints with cookie-based JWT."""

from fastapi import APIRouter, HTTPException, Depends, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.models.user import User
from app.schemas.user import UserCreate, LoginForm
from app.crud.user import create_user
from app.auth.jwt import (
    create_tokens,
    decode_token,
    set_auth_cookies,
    clear_auth_cookies,
    get_current_user,
    TokenType,
)
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserInfo(BaseModel):
    """User info for token response."""

    id: int
    username: str
    email: str
    first_name: str | None = None
    last_name: str | None = None
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    picture: str | None = None
    phone: str | None = None


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo | None = None


class MessageResponse(BaseModel):
    """Simple message response."""

    message: str


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account and return authentication tokens.",
)
async def register(user: UserCreate, response: Response):
    """Register a new user.

    Creates a new user account and sets authentication cookies.
    Also returns tokens in the response body for API clients.

    Args:
        user: User registration data
        response: FastAPI Response object

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username exists
    if await User.filter(username=user.username).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    if await User.filter(email=user.email).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create user
    new_user = await create_user(user)

    # Create tokens
    access_token, refresh_token = create_tokens(new_user.username)

    # Set cookies
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            is_active=new_user.is_active,
            is_staff=new_user.is_staff,
            is_superuser=new_user.is_superuser,
            picture=new_user.picture,
            phone=new_user.phone,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login with OAuth2 form",
    description="Authenticate user with username and password form data.",
)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with OAuth2 password form.

    This is the standard OAuth2 password flow endpoint.
    Compatible with Swagger UI authentication.

    Args:
        response: FastAPI Response object
        form_data: OAuth2 form data with username and password

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user = await User.get_or_none(username=form_data.username)

    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    access_token, refresh_token = create_tokens(user.username)
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            picture=user.picture,
            phone=user.phone,
        ),
    )


@router.post(
    "/login-form",
    response_model=TokenResponse,
    summary="Login with form data",
    description="Authenticate user with username and password form data.",
)
async def login_form(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
):
    """Login with form data (alias for /login)."""
    return await login(response, form_data)


@router.post(
    "/login-json",
    response_model=TokenResponse,
    summary="Login with JSON",
    description="Authenticate user with JSON body.",
)
async def login_json(form_data: LoginForm, response: Response):
    """Login with JSON body.

    Args:
        form_data: Login credentials as JSON
        response: FastAPI Response object

    Returns:
        TokenResponse with access and refresh tokens

    Raises:
        HTTPException: If credentials are invalid
    """
    user = await User.get_or_none(username=form_data.username)

    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    access_token, refresh_token = create_tokens(user.username)
    set_auth_cookies(response, access_token, refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            picture=user.picture,
            phone=user.phone,
        ),
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Get a new access token using refresh token from cookie.",
)
async def refresh_token(request: Request, response: Response):
    """Refresh access token using refresh token.

    Uses the refresh token from cookie to issue a new access token.

    Args:
        request: FastAPI Request object
        response: FastAPI Response object

    Returns:
        TokenResponse with new access token

    Raises:
        HTTPException: If refresh token is invalid or expired
    """
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
        )

    # Validate refresh token
    payload = decode_token(refresh_token, TokenType.REFRESH)
    username = payload.get("sub")

    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Verify user still exists and is active
    user = await User.get_or_none(username=username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled",
        )

    # Create new tokens
    access_token, new_refresh_token = create_tokens(user.username)
    set_auth_cookies(response, access_token, new_refresh_token)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserInfo(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            is_staff=user.is_staff,
            is_superuser=user.is_superuser,
            picture=user.picture,
            phone=user.phone,
        ),
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Logout user",
    description="Clear authentication cookies and logout user.",
)
async def logout(response: Response):
    """Logout user by clearing authentication cookies.

    Args:
        response: FastAPI Response object

    Returns:
        Success message
    """
    clear_auth_cookies(response)
    return MessageResponse(message="Successfully logged out")


@router.get(
    "/me",
    summary="Get current user",
    description="Get details of the currently authenticated user.",
)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user details.

    Args:
        current_user: Current authenticated user

    Returns:
        User details
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "is_active": current_user.is_active,
        "is_staff": current_user.is_staff,
        "is_superuser": current_user.is_superuser,
        "picture": current_user.picture,
        "phone": current_user.phone,
        "created": current_user.created,
    }
