"""Main FastAPI application module."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
import os
import time
import uuid

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, FileResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from tortoise import Tortoise

from app.database import init
from app.routers import user, post, comment, comment_likes, likes, images
from app.auth import auth
from app.config import settings
from app.core.logging_config import setup_logging
from app.core.exceptions import AppException

# Configure FastAdmin settings before importing
# ADMIN_USER_MODEL should be the ORM model class name (User), not the Admin class name
os.environ.setdefault("ADMIN_USER_MODEL", "User")
os.environ.setdefault("ADMIN_USER_MODEL_USERNAME_FIELD", "username")
os.environ.setdefault("ADMIN_SECRET_KEY", settings.JWT_SECRET_KEY)

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Use uvloop only if not in test mode
if not os.environ.get("PYTEST_CURRENT_TEST"):
    try:
        import uvloop
        import asyncio

        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        logger.info("Using uvloop for better performance")
    except ImportError:
        logger.info("uvloop not available, using default event loop")

BASE_DIR = settings.BASE_DIR
FAVICON_PATH = BASE_DIR / "app" / "static" / "favicon.png"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator:
    """Application lifespan manager.

    Handles startup and shutdown events for the FastAPI application.
    """
    logger.info(f"Starting up: Initializing {application.title}...")

    try:
        await init()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Ensure upload directory exists
    settings.UPLOAD_DIR.mkdir(exist_ok=True)
    logger.info(f"Upload directory ready: {settings.UPLOAD_DIR}")

    yield

    logger.info("Shutting down: Closing database connections...")
    try:
        await Tortoise.close_connections()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A robust API for managing blog posts. Users can register, create posts, "
        "leave comments, add likes, and upload images. "
        "The API supports cookie-based JWT authentication with refresh tokens."
    ),
    version=settings.APP_VERSION,
    contact={
        "name": "Matnazar Matnazarov",
        "url": "https://github.com/Matnazar-Matnazarov",
        "email": "matnazarmatnazarov3@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    debug=settings.DEBUG,
)


# CORS Middleware - configured for cookie-based auth
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
    expose_headers=settings.CORS_EXPOSE_HEADERS,
    max_age=settings.CORS_MAX_AGE,
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


# Add request ID middleware
app.add_middleware(RequestIDMiddleware)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to responses."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Process-Time-ms"] = f"{process_time:.3f}"
    return response


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"[{request_id}] AppException: {exc.detail} - Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"[{request_id}] HTTPException: {exc.detail} - Status: {exc.status_code} - Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "request_id": request_id},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.warning(
        f"[{request_id}] ValidationError: {exc.errors()} - Path: {request.url.path}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "request_id": request_id},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        f"[{request_id}] Unexpected error: {exc} - Path: {request.url.path}",
        exc_info=True,
    )

    # Don't expose internal errors in production
    detail = "Internal server error"
    if settings.DEBUG:
        detail = str(exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": detail, "request_id": request_id},
    )


# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(post.router)
app.include_router(comment.router)
app.include_router(comment_likes.router)
app.include_router(likes.router)
app.include_router(images.router)


@app.get("/", summary="Root endpoint", description="The main endpoint of the API.")
async def root():
    """Root endpoint providing API information."""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "redoc": "/redoc",
        "admin": "/admin",
    }


@app.get("/health", summary="Health check", description="Check API health status.")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon."""
    if FAVICON_PATH.exists():
        return FileResponse(FAVICON_PATH)
    return JSONResponse(status_code=404, content={"detail": "Favicon not found"})


def custom_openapi():
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
        "backgroundColor": "#FFFFFF",
    }

    openapi_schema["servers"] = [
        {"url": "http://127.0.0.1:8000", "description": "Local Development Server"},
    ]

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/auth/login",
                    "scopes": {},
                }
            },
        },
        "cookieAuth": {
            "type": "apiKey",
            "in": "cookie",
            "name": "access_token",
        },
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Mount admin app if available
try:
    # Import admin module FIRST to register models and set settings
    from app import admin as admin_config  # noqa: F401
    from fastadmin import fastapi_app as admin_fastapi_app

    app.mount("/admin", admin_fastapi_app)
    logger.info("Admin panel mounted at /admin")
except ImportError as e:
    logger.warning(f"FastAdmin not available, admin panel disabled: {e}")

# Custom OpenAPI schema
app.openapi = custom_openapi
