# 🚀 Blog Post API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A modern, production-ready REST API for blog management built with FastAPI and Tortoise ORM**

[Features](#-features) • [Quick Start](#-quick-start) • [API Docs](#-api-documentation) • [Development](#-development) • [Testing](#-testing)

</div>

---

## ✨ Features

### Core Features
- 📝 **Blog Posts** - Create, read, update, delete posts with image support
- 💬 **Comments** - Nested comment system with user attribution
- ❤️ **Likes** - Like/unlike posts and comments
- 🖼️ **Images** - Upload and manage post images with validation

### Authentication & Security
- 🔐 **JWT Authentication** - Secure token-based auth with access/refresh tokens
- 🍪 **Cookie-based Sessions** - HttpOnly secure cookies for web clients
- 👮 **Role-based Access** - User, Staff, and Superuser roles
- 🛡️ **CORS Protection** - Configurable cross-origin resource sharing

### Developer Experience
- 📚 **OpenAPI Documentation** - Interactive Swagger UI & ReDoc
- 🎛️ **Admin Panel** - FastAdmin integration for data management
- 🔄 **Database Migrations** - Aerich for schema versioning
- ✅ **Comprehensive Tests** - 55+ async tests with pytest
- 📊 **Logging** - Colored console logs (dev) + file rotation (prod)
- ⚡ **High Performance** - uvloop for faster async operations

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **Framework** | FastAPI 0.115+ |
| **ORM** | Tortoise ORM 0.24+ |
| **Database** | PostgreSQL 15+ |
| **Authentication** | PyJWT + Passlib (bcrypt) |
| **Validation** | Pydantic V2 |
| **Migrations** | Aerich |
| **Testing** | Pytest + HTTPX + pytest-asyncio |
| **Admin** | FastAdmin |
| **Linting** | Ruff |
| **Performance** | uvloop |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/FastAPI-Tortoise.git
cd FastAPI-Tortoise
```

2. **Create virtual environment and install dependencies**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials and secret key
```

4. **Create databases**
```bash
# Create main and test databases in PostgreSQL
createdb blog_post
createdb blog_post_test
```

5. **Run database migrations**
```bash
uv run aerich upgrade
```

6. **Seed initial users (optional)**
```bash
uv run python -m app.scripts.seed_users
```

7. **Start the server**
```bash
# Development mode with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

8. **Open in browser**
- API Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Admin Panel: http://localhost:8000/admin

---

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login with JSON body |
| `POST` | `/auth/login-form` | Login with form data |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Logout (clear cookies) |
| `GET` | `/auth/me` | Get current user info |

### User Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/users/` | List all users | Staff |
| `GET` | `/users/{id}` | Get user by ID | Staff |
| `POST` | `/users/` | Create new user | Staff |

### Post Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/posts/` | List all posts | Staff |
| `GET` | `/posts/{id}` | Get post by ID | Owner/Staff |
| `POST` | `/posts/` | Create new post | User |
| `PUT` | `/posts/{id}` | Update post | Owner/Staff |
| `DELETE` | `/posts/{id}` | Delete post | Owner/Staff |

### Comment Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/comments/{id}` | Get comment by ID | Owner/Staff |
| `POST` | `/comments/{post_id}` | Add comment to post | User |
| `DELETE` | `/comments/{id}` | Delete comment | Owner/Staff |

### Like Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| `GET` | `/likes/{id}` | Get like by ID | Owner/Staff |
| `POST` | `/likes/{post_id}` | Like a post | User |
| `POST` | `/comment-likes/{comment_id}` | Like a comment | User |

---

## 💻 Development

### Project Structure

```
FastAPI-Tortoise/
├── app/
│   ├── auth/           # Authentication (JWT, routes)
│   ├── core/           # Core utilities (exceptions, security, logging)
│   ├── crud/           # Database operations
│   ├── models/         # Tortoise ORM models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic schemas
│   ├── scripts/        # Utility scripts (seed_users)
│   ├── static/         # Static files
│   ├── admin.py        # FastAdmin configuration
│   ├── config.py       # Application settings
│   ├── database.py     # Database configuration
│   └── main.py         # FastAPI application
├── migrations/         # Aerich migrations
├── tests/              # Test suite
├── logs/               # Log files (auto-created)
├── uploads/            # Uploaded images (auto-created)
├── .env.example        # Environment template
├── pyproject.toml      # Project dependencies
├── pytest.ini          # Pytest configuration
└── README.md
```

### Running in Development Mode

Development mode enables:
- 🎨 Colored console logs
- 🐛 Debug level logging
- 📋 Detailed error messages
- 🔄 Auto-reload on file changes

```bash
# Set DEBUG=true in .env, then:
uv run uvicorn app.main:app --reload
```

### Code Quality

```bash
# Run linter
uv run ruff check .

# Auto-fix issues
uv run ruff check --fix .

# Format code
uv run ruff format .
```

### Database Migrations

```bash
# Create new migration
uv run aerich migrate --name "description"

# Apply migrations
uv run aerich upgrade

# Rollback last migration
uv run aerich downgrade
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_auth.py

# Run with coverage report
uv run pytest --cov=app --cov-report=html
```

### Test Database

Tests use a separate PostgreSQL database configured via `TEST_DATABASE_URL` in `.env`.

```bash
# Create test database
createdb blog_post_test
```

---

## 🎛️ Admin Panel

Access the admin panel at http://localhost:8000/admin

### Default Credentials
- **Username:** `admin`
- **Password:** `AdminPassword123!`

### Creating Admin User

```bash
uv run python -m app.scripts.seed_users
```

This creates:
- `admin` - Superuser with full access
- `staff` - Staff user with elevated permissions
- `demo` - Regular user for testing

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `SECRET_KEY` | JWT signing key (32+ chars) | Required |
| `DEBUG` | Enable debug mode | `false` |
| `ENVIRONMENT` | `development`, `staging`, `production` | `development` |
| `TIMEZONE` | Application timezone | `Asia/Tashkent` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `CORS_ORIGINS` | Allowed CORS origins | `localhost` |
| `COOKIE_SECURE` | HTTPS-only cookies | `false` |
| `MAX_UPLOAD_SIZE` | Max file upload size (bytes) | `2097152` |

See `.env.example` for complete configuration options.

---

## 📊 Logging

### Development Mode
- Colored console output
- Debug level logging
- All request details visible

### Production Mode
- Minimal console output
- Info level logging
- Rotating file logs in `logs/` directory:
  - `app.log` - All logs (10MB rotation, 5 backups)
  - `error.log` - Errors only

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Matnazar Matnazarov**

- GitHub: [@Matnazar-Matnazarov](https://github.com/Matnazar-Matnazarov)
- Email: matnazarmatnazarov3@gmail.com

---

<div align="center">
Made with ❤️ using FastAPI
</div>
