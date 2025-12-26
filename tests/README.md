# Test Documentation

Bu loyiha uchun professional strukturada yozilgan pytest testlari.

## Test Strukturasi

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures va konfiguratsiya
├── test_auth.py         # Authentication endpoint testlari
├── test_users.py        # User endpoint testlari
├── test_posts.py         # Post endpoint testlari
├── test_comments.py     # Comment endpoint testlari
├── test_likes.py        # Like endpoint testlari
├── test_comment_likes.py # Comment like endpoint testlari
└── test_images.py       # Image endpoint testlari
```

## Test Database

Testlar PostgreSQL database ishlatadi. Test database URL `TEST_DATABASE_URL` environment variable orqali belgilanadi.

Default: `postgres://postgres:password@localhost:5432/blog_post_test`

**Eslatma**: Test database alohida bo'lishi kerak, production database emas!

## Testlarni Ishga Tushirish

### Environment Variable Sozlash

```bash
export TEST_DATABASE_URL="postgres://postgres:password@localhost:5432/blog_post_test"
```

Yoki `.env` faylida:
```env
TEST_DATABASE_URL=postgres://postgres:password@localhost:5432/blog_post_test
```

### Test Database Yaratish

```bash
# PostgreSQL'da test database yaratish
createdb blog_post_test

# Yoki psql orqali
psql -U postgres -c "CREATE DATABASE blog_post_test;"
```

### Barcha testlarni ishga tushirish:
```bash
pytest
```

### Faqat bitta fayl testlarini ishga tushirish:
```bash
pytest tests/test_auth.py
```

### Coverage bilan testlarni ishga tushirish:
```bash
pytest --cov=app --cov-report=html
```

### Verbose rejimda:
```bash
pytest -v
```

## Test Coverage

Har bir endpoint uchun quyidagi testlar yozilgan:

1. **Muvaffaqiyatli so'rovlar** - 200/201 status kodlari
2. **Noto'g'ri autentifikatsiya** - 401 status kodi
3. **Yetarli huquqlar yo'q** - 403 status kodi
4. **Topilmadi** - 404 status kodi
5. **Validation xatolari** - 422 status kodi
6. **Konfliktlar** - 409 status kodi (qayerda kerak bo'lsa)

## Test Fixtures

`conftest.py` faylida quyidagi fixtures mavjud:

- `client` - AsyncClient fixture (function scope, async client)
- `initialize_db` - Database initialization (session scope, autouse)
- `clean_db` - Database cleanup (function scope, autouse)
- `test_user` - Oddiy foydalanuvchi (unique identifier bilan)
- `test_staff_user` - Staff foydalanuvchi (unique identifier bilan)
- `test_superuser` - Superuser (unique identifier bilan)
- `test_user_token` - JWT token (oddiy foydalanuvchi uchun)
- `test_staff_token` - JWT token (staff uchun)
- `test_superuser_token` - JWT token (superuser uchun)
- `test_post` - Test post
- `test_comment` - Test comment
- `test_like` - Test like
- `test_comment_like` - Test comment like

## Database Cleanup

Har bir testdan keyin database avtomatik ravishda tozalanadi (`clean_db` fixture). Bu UNIQUE constraint xatolarini oldini oladi.

## Test Maqsadlari

1. **Xavfsizlik** - Barcha endpointlar to'g'ri autentifikatsiya va autorizatsiyani talab qiladi
2. **Validation** - Barcha input ma'lumotlari to'g'ri validatsiya qilinadi
3. **Error Handling** - Barcha xatolar to'g'ri handle qilinadi
4. **Business Logic** - Business logic to'g'ri ishlaydi

## Eslatmalar

- Testlar PostgreSQL database ishlatadi (production database emas!)
- Har bir test o'zidan oldingi testlardan mustaqil
- Test funksiyalar async (`httpx.AsyncClient` ishlatiladi)
- Barcha operatsiyalar bir xil event loop'da bajariladi
- `pytest-asyncio` bilan `asyncio_mode = auto` ishlatiladi
- `uvloop` testlar uchun o'chirilgan (default asyncio ishlatiladi)
- Har bir testdan keyin database tozalanadi
- Har bir user fixture unique identifier ishlatadi
