from tortoise import Tortoise
from environs import Env
import logging

logger = logging.getLogger(__name__)

env = Env()
env.read_env()

DATABASE_URL = env.str("DATABASE_URL")

# Tortoise ORM requires 'postgres' not 'postgresql' in the URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgres://", 1)
    logger.info("Converted postgresql:// to postgres:// for Tortoise ORM compatibility")

TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.post",
                "app.models.comment",
                "app.models.comment_likes",
                "app.models.likes",
                "app.models.images",
                "app.models.post_view",
                "aerich.models",
            ],
            "default_connection": "default",
        },
    },
}


async def init():
    """Initialize Tortoise ORM database connection."""
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
