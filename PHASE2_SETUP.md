# راهنمای فاز ۲: مدل داده‌ها / Phase 2: Data Models Guide

## ✅ کارهای انجام شده

### ۱. ایجاد Enums
- `UserRole`: نقش‌های کاربر (ADMIN, USER)
- `Language`: زبان‌های پشتیبانی شده (FA, EN)
- `TicketCategory`: دسته‌بندی تیکت‌ها (INTERNET, EQUIPMENT, SOFTWARE, OTHER)
- `TicketStatus`: وضعیت تیکت‌ها (PENDING, IN_PROGRESS, RESOLVED, CLOSED)

### ۲. ایجاد مدل User
- فیلدها: id, username, full_name, password_hash, role, language, is_active
- Timestamps: created_at, updated_at
- Relationship: tickets (One-to-Many با Ticket)

### ۳. ایجاد مدل Ticket
- فیلدها: id, ticket_number, title, description, category, status, user_id
- Timestamps: created_at, updated_at
- Relationship: user (Many-to-One با User)
- Indexes: برای بهینه‌سازی کوئری‌ها

### ۴. ایجاد Security Utilities
- `get_password_hash`: Hash کردن رمز عبور
- `verify_password`: بررسی رمز عبور
- `create_access_token`: ایجاد JWT Token
- `decode_access_token`: Decode کردن JWT Token

### ۵. ایجاد Scripts
- `scripts/init_db.py`: ایجاد جداول دیتابیس
- `scripts/create_admin.py`: ایجاد کاربر ادمین
- `scripts/test_models.py`: تست مدل‌ها

## 🚀 مراحل راه‌اندازی

### مرحله ۱: ایجاد جداول دیتابیس

**مهم**: مطمئن شوید که Virtual Environment فعال است!

```bash
# روش ۱: استفاده از Python از virtual environment
.venv\Scripts\python.exe scripts\init_db.py

# روش ۲: فعال‌سازی virtual environment و سپس اجرا
.venv\Scripts\activate
python scripts\init_db.py
```

این دستور تمام جداول را در دیتابیس SQLite ایجاد می‌کند.

### مرحله ۲: ایجاد کاربر ادمین

```bash
# روش ۱: استفاده از Python از virtual environment
.venv\Scripts\python.exe scripts\create_admin.py

# روش ۲: فعال‌سازی virtual environment و سپس اجرا
.venv\Scripts\activate
python scripts\create_admin.py
```

یا با مقادیر دلخواه:
```bash
python scripts/create_admin.py admin mypassword "مدیر سیستم"
```

### مرحله ۳: تست مدل‌ها

```bash
# روش ۱: استفاده از Python از virtual environment
.venv\Scripts\python.exe scripts\test_models.py

# روش ۲: فعال‌سازی virtual environment و سپس اجرا
.venv\Scripts\activate
python scripts\test_models.py
```

این اسکریپت مدل‌ها را تست می‌کند و داده‌های نمونه ایجاد می‌کند.

## 📁 ساختار فایل‌های ایجاد شده

```
app/
├── core/
│   ├── enums.py          ✅ Enums
│   └── security.py       ✅ Security utilities
├── models/
│   ├── __init__.py       ✅ Models exports
│   ├── user.py           ✅ User model
│   └── ticket.py         ✅ Ticket model
└── scripts/
    ├── init_db.py        ✅ Initialize database
    ├── create_admin.py   ✅ Create admin user
    └── test_models.py    ✅ Test models
```

## 🔍 بررسی دیتابیس

پس از ایجاد جداول، می‌توانید فایل `ticketing.db` را با یک SQLite Browser (مثل DB Browser for SQLite) باز کنید و ساختار جداول را مشاهده کنید.

### جداول ایجاد شده:
1. **users**: کاربران سیستم
2. **tickets**: تیکت‌ها

## 📊 Schema دیتابیس

### جدول users
- `id` (INTEGER, PRIMARY KEY)
- `username` (VARCHAR, UNIQUE, INDEXED)
- `full_name` (VARCHAR)
- `password_hash` (VARCHAR)
- `role` (VARCHAR, ENUM)
- `language` (VARCHAR, ENUM)
- `is_active` (BOOLEAN)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

### جدول tickets
- `id` (INTEGER, PRIMARY KEY)
- `ticket_number` (VARCHAR, UNIQUE, INDEXED)
- `title` (VARCHAR)
- `description` (TEXT)
- `category` (VARCHAR, ENUM)
- `status` (VARCHAR, ENUM)
- `user_id` (INTEGER, FOREIGN KEY)
- `created_at` (DATETIME)
- `updated_at` (DATETIME)

## ✅ چک‌لیست

- [ ] جداول دیتابیس ایجاد شده
- [ ] کاربر ادمین ایجاد شده
- [ ] مدل‌ها تست شده‌اند
- [ ] روابط بین مدل‌ها کار می‌کنند
- [ ] Indexes ایجاد شده‌اند

## 🐛 عیب‌یابی

### مشکل: خطای Import یا ModuleNotFoundError
**راه‌حل**: 
1. مطمئن شوید که Virtual Environment فعال است
2. از `.venv\Scripts\python.exe` برای اجرای اسکریپت‌ها استفاده کنید
3. یا Virtual Environment را فعال کنید: `.venv\Scripts\activate`

### مشکل: Circular Import
**راه‌حل**: این مشکل حل شده است. اگر باز هم رخ داد، مطمئن شوید که از آخرین نسخه فایل‌ها استفاده می‌کنید.

### مشکل: خطای ایجاد جداول
**راه‌حل**: مطمئن شوید که فایل `ticketing.db` موجود نیست یا آن را حذف کنید و دوباره اجرا کنید.

### مشکل: خطای Foreign Key
**راه‌حل**: مطمئن شوید که ابتدا User ایجاد شده است قبل از ایجاد Ticket.

## 🎯 مراحل بعدی

پس از تکمیل فاز ۲، می‌توانید به فاز ۳ بروید:
- **فاز ۳**: سیستم احراز هویت (Authentication System)

---

**تاریخ تکمیل**: 2024-11-11

