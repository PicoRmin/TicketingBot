# راهنمای فاز ۳: سیستم احراز هویت / Phase 3: Authentication System Guide

## ✅ کارهای انجام شده

### ۱. ایجاد Schemas
- ✅ `UserBase` - شامل زبان و شناسه شعبه (`branch_id`)
- ✅ `UserCreate` - Schema برای ایجاد کاربر با نقش و شعبه
- ✅ `UserUpdate` - Schema برای به‌روزرسانی کاربر (نقش/شعبه)
- ✅ `UserResponse` - Schema برای پاسخ API
- ✅ `LoginRequest` - Schema برای درخواست Login
- ✅ `Token` - Schema برای Token response (شامل `refresh_token` و `expires_in`)
- ✅ `TokenData` - Schema برای داده‌های Token (user_id، role، branch_id)
- ✅ `RefreshTokenRequest` - Schema برای تازه‌سازی / خروج از سیستم

### ۲. ایجاد Dependencies
- ✅ `get_current_user` - دریافت کاربر فعلی از Token
- ✅ `get_current_active_user` - دریافت کاربر فعال فعلی
- ✅ `require_roles` - وابستگی عمومی برای نقش‌ها
- ✅ `require_admin` - نقش‌های `admin` و `central_admin`
- ✅ `require_central_admin` - نقش مرکزی
- ✅ `require_branch_admin` - نقش مدیر شعبه
- ✅ `require_report_access` - نقش‌های مجاز برای گزارش‌ها (report_manager، admin، central_admin)

### ۳. ایجاد API Endpoints
- ✅ `POST /api/auth/login` - Login با OAuth2PasswordRequestForm (برمی‌گرداند access/refresh token)
- ✅ `POST /api/auth/login-form` - Login با JSON form data
- ✅ `POST /api/auth/refresh` - صدور access token جدید با refresh token
- ✅ `POST /api/auth/logout` - ابطال refresh token
- ✅ `POST /api/auth/link-telegram` - لینک کردن حساب تلگرام
- ✅ `GET /api/auth/me` - دریافت اطلاعات کاربر فعلی

### ۴. ایجاد API Router
- ✅ `app/api/auth.py` - Router برای Authentication
- ✅ اضافه شدن router به `main.py`

### ۵. حل مشکلات
- ✅ CORS_ORIGINS - حل شده
- ✅ verify_password - ساده‌سازی شده

## 🚀 تست Authentication

### تست با Swagger UI

1. **اجرای Application**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **باز کردن Swagger UI**:
   - آدرس: http://localhost:8000/docs

3. **تست Login**:
   - کلیک روی `POST /api/auth/login`
   - وارد کردن `username` و `password`
   - پاسخ شامل `access_token`, `refresh_token`, `expires_in`

4. **تست Get Current User**:
   - کلیک روی "Authorize" در بالای صفحه
   - وارد کردن Token: `Bearer <access_token>`
   - کلیک روی "Authorize"
   - کلیک روی `GET /api/auth/me`
   - کلیک روی "Execute"
   - مشاهده اطلاعات کاربر

### تست با curl

```bash
# 1. Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# پاسخ:
# {"access_token":"...","refresh_token":"...","token_type":"bearer","expires_in":86400}

# 2. Refresh token
curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'

# 3. Logout (revoke refresh token)
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<refresh_token>"}'
```

### تست با Python

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    data={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Get Current User
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/auth/me",
    headers=headers
)
print(response.json())
```

## 📁 ساختار فایل‌های ایجاد شده

```
app/
├── api/
│   ├── __init__.py        ✅ API exports
│   ├── auth.py            ✅ Authentication endpoints
│   └── deps.py            ✅ Dependencies
├── schemas/
│   ├── __init__.py        ✅ Schema exports
│   ├── user.py            ✅ User schemas
│   └── token.py           ✅ Token schemas
└── main.py                ✅ Updated with auth router
```

## 🔍 API Endpoints

### POST /api/auth/login
- **Description**: Login با OAuth2PasswordRequestForm
- **Request**: `username`, `password` (form data)
- **Response**: `{"access_token": "...", "token_type": "bearer"}`
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

### POST /api/auth/login-form
- **Description**: Login با JSON form data
- **Request**: `{"username": "...", "password": "..."}`
- **Response**: `{"access_token": "...", "token_type": "bearer"}`
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

### GET /api/auth/me
- **Description**: دریافت اطلاعات کاربر فعلی
- **Headers**: `Authorization: Bearer <token>`
- **Response**: User information
- **Status Codes**: 200 (success), 401 (unauthorized), 400 (inactive user)

## 🔐 Security

### JWT Token
- **Algorithm**: HS256
- **Expiration**: 1440 دقیقه (24 ساعت)
- **Payload**: `{"sub": username, "user_id": id, "role": role, "branch_id": branch_id}`

### Refresh Tokens
- **ساختار**: توکن تصادفی، ذخیره شده به صورت hash در جدول `refresh_tokens`
- **انقضا**: ۱۴ روز (قابل تنظیم با `REFRESH_TOKEN_EXPIRE_DAYS`)
- **چرخش**: در هر `refresh` توکن جدید صادر و قبلی ابطال می‌شود
- **خروج**: `POST /api/auth/logout`

### Password Hashing
- **Algorithm**: bcrypt
- **Salt**: Auto-generated
- **Verification**: Direct bcrypt verification

## ✅ چک‌لیست

- [x] Schemas ایجاد شده
- [x] Dependencies ایجاد شده
- [x] API Endpoints ایجاد شده
- [x] Router اضافه شده به main.py
- [x] تست با Swagger UI
- [x] تست با curl
- [x] تست با Python

## 🐛 عیب‌یابی

### مشکل: 401 Unauthorized
**راه‌حل**: مطمئن شوید که username و password صحیح است.

### مشکل: Token invalid
**راه‌حل**: مطمئن شوید که Token را به درستی در Header قرار داده‌اید:
```
Authorization: Bearer <token>
```

### مشکل: Inactive user
**راه‌حل**: مطمئن شوید که کاربر `is_active=True` است.

## 🎯 مراحل بعدی

پس از تکمیل فاز ۳، می‌توانید به فاز ۴ بروید:
- **فاز ۴**: API Core - مدیریت تیکت‌ها

## 🔍 مهاجرت دیتابیس مرتبط
```bash
python scripts/migrate_v8_add_user_branch.py
python scripts/migrate_v9_create_refresh_tokens.py
```
(در صورت اجرای نسخه‌های قبل، تنها اسکریپت‌های جدید لازم است.)

---

**تاریخ تکمیل**: 2025-11-12

