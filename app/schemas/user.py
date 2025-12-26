"""User schemas for API validation."""

from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional
from app.config import settings
from app.core.security import validate_email, validate_password_strength


class UserBase(BaseModel):
    """Base user schema."""

    username: str = Field(..., min_length=3, max_length=50, description="Username")
    first_name: str = Field(..., min_length=1, max_length=255, description="First name")
    last_name: str = Field(..., min_length=1, max_length=255, description="Last name")
    email: EmailStr = Field(..., description="Email address")
    is_active: bool = Field(default=True, description="User active status")
    is_staff: bool = Field(default=False, description="Staff status")
    picture: Optional[str] = Field(
        None, max_length=255, description="Profile picture URL"
    )
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format."""
        if not validate_email(v):
            raise ValueError("Invalid email format")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username format."""
        if not v.isalnum() and "_" not in v:
            raise ValueError(
                "Username must contain only alphanumeric characters and underscores"
            )
        return v


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(
        ..., min_length=settings.PASSWORD_MIN_LENGTH, description="Password"
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        is_valid, error_message = validate_password_strength(v)
        if not is_valid:
            raise ValueError(error_message)
        return v


class User(UserBase):
    """User response schema."""

    id: int
    created: datetime

    model_config = ConfigDict(from_attributes=True)


class LoginForm(BaseModel):
    """Login form schema."""

    username: str
    password: str
