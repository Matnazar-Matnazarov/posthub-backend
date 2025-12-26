"""Seed database with initial users including admin.

Usage:
    python -m app.scripts.seed_users

Or via uv:
    uv run python -m app.scripts.seed_users
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tortoise import Tortoise
from app.models.user import User
from app.config import settings
from app.database import TORTOISE_ORM


async def create_superuser(
    username: str,
    email: str,
    password: str,
    first_name: str = "Admin",
    last_name: str = "User",
) -> User:
    """Create a superuser.

    Args:
        username: Admin username
        email: Admin email
        password: Admin password
        first_name: First name
        last_name: Last name

    Returns:
        Created User instance
    """
    user = await User.get_or_none(username=username)

    if user:
        print(f"User '{username}' already exists. Updating to superuser...")
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.set_password(password)
        await user.save()
        return user

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_staff=True,
        is_superuser=True,
    )
    user.set_password(password)
    await user.save()

    print(f"Superuser '{username}' created successfully!")
    return user


async def create_staff_user(
    username: str,
    email: str,
    password: str,
    first_name: str = "Staff",
    last_name: str = "User",
) -> User:
    """Create a staff user.

    Args:
        username: Staff username
        email: Staff email
        password: Staff password
        first_name: First name
        last_name: Last name

    Returns:
        Created User instance
    """
    user = await User.get_or_none(username=username)

    if user:
        print(f"User '{username}' already exists. Skipping...")
        return user

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_staff=True,
        is_superuser=False,
    )
    user.set_password(password)
    await user.save()

    print(f"Staff user '{username}' created successfully!")
    return user


async def create_regular_user(
    username: str,
    email: str,
    password: str,
    first_name: str = "Regular",
    last_name: str = "User",
) -> User:
    """Create a regular user.

    Args:
        username: Username
        email: Email
        password: Password
        first_name: First name
        last_name: Last name

    Returns:
        Created User instance
    """
    user = await User.get_or_none(username=username)

    if user:
        print(f"User '{username}' already exists. Skipping...")
        return user

    user = User(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        is_active=True,
        is_staff=False,
        is_superuser=False,
    )
    user.set_password(password)
    await user.save()

    print(f"Regular user '{username}' created successfully!")
    return user


async def seed_users():
    """Seed database with initial users."""
    print("=" * 50)
    print("Seeding users...")
    print("=" * 50)

    # Create superuser from settings
    await create_superuser(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        password=settings.ADMIN_PASSWORD,
        first_name="Admin",
        last_name="User",
    )

    # Create additional staff user
    await create_staff_user(
        username="staff",
        email="staff@example.com",
        password="StaffPassword123!",
        first_name="Staff",
        last_name="Member",
    )

    # Create demo regular user
    await create_regular_user(
        username="demo",
        email="demo@example.com",
        password="DemoPassword123!",
        first_name="Demo",
        last_name="User",
    )

    print("=" * 50)
    print("Seeding complete!")
    print("=" * 50)
    print("\nCreated users:")
    print(f"  - Admin: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
    print("  - Staff: staff / StaffPassword123!")
    print("  - Demo:  demo / DemoPassword123!")
    print()


async def main():
    """Main entry point."""
    print("Connecting to database...")

    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()

    try:
        await seed_users()
    finally:
        await Tortoise.close_connections()
        print("Database connection closed.")


if __name__ == "__main__":
    asyncio.run(main())
