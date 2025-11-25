# 📋 راهنمای تست‌ها - سیستم تیکتینگ ایرانمهر

## فهرست مطالب
1. [معرفی](#معرفی)
2. [ساختار تست‌ها](#ساختار-تست‌ها)
3. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
4. [اجرای تست‌ها](#اجرای-تست‌ها)
5. [انواع تست‌ها](#انواع-تست‌ها)
6. [نوشتن تست جدید](#نوشتن-تست-جدید)
7. [Coverage](#coverage)
8. [بهترین روش‌ها](#بهترین-روش‌ها)

---

## معرفی

این دایرکتوری شامل تمام تست‌های واحد (Unit Tests) و تست‌های یکپارچه‌سازی (Integration Tests) برای سیستم تیکتینگ ایرانمهر است.

### ابزارهای استفاده شده:
- **pytest**: فریمورک تست اصلی
- **pytest-asyncio**: برای تست‌های async
- **pytest-cov**: برای اندازه‌گیری Coverage
- **httpx**: برای تست API endpoints

---

## ساختار تست‌ها

```
tests/
├── __init__.py
├── conftest.py              # Fixtures و تنظیمات مشترک
├── README.md                # این فایل
│
├── test_models.py           # تست‌های اولیه Models
├── test_models_complete.py  # تست‌های کامل Models
│
├── test_services.py         # تست‌های اولیه Services
├── test_services_complete.py # تست‌های کامل Services
│
├── test_api.py              # تست‌های API Endpoints
│
├── test_custom_fields.py    # تست‌های Custom Fields
├── test_custom_fields_api.py # تست‌های API Custom Fields
│
├── test_email_service.py    # تست‌های Email Service
│
└── test_security.py         # تست‌های امنیتی
```

---

## نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
# نصب pytest و ابزارهای تست
pip install -r requirements.txt

# یا فقط ابزارهای تست
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. بررسی تنظیمات

فایل `pytest.ini` در ریشه پروژه تنظیمات pytest را شامل می‌شود.

---

## اجرای تست‌ها

### اجرای تمام تست‌ها

```bash
# اجرای تمام تست‌ها
pytest

# با نمایش جزئیات
pytest -v

# با نمایش خروجی print
pytest -s
```

### اجرای تست‌های خاص

```bash
# اجرای یک فایل تست
pytest tests/test_models.py

# اجرای یک کلاس تست
pytest tests/test_models.py::TestUserModel

# اجرای یک تابع تست
pytest tests/test_models.py::TestUserModel::test_user_creation
```

### اجرای با Coverage

```bash
# اجرای با Coverage
pytest --cov=app --cov-report=html

# مشاهده گزارش Coverage
# فایل htmlcov/index.html را در مرورگر باز کنید
```

### اجرای با Markers

```bash
# فقط تست‌های واحد
pytest -m unit

# فقط تست‌های یکپارچه‌سازی
pytest -m integration

# فقط تست‌های API
pytest -m api
```

---

## انواع تست‌ها

### 1. Unit Tests (تست‌های واحد)

تست‌های واحد برای تست کردن توابع و کلاس‌ها به صورت جداگانه:

```python
def test_user_creation(db, test_user):
    """تست ایجاد کاربر"""
    assert test_user.id is not None
    assert test_user.username == "testuser"
```

**فایل‌ها:**
- `test_models.py` / `test_models_complete.py`
- `test_services.py` / `test_services_complete.py`

### 2. Integration Tests (تست‌های یکپارچه‌سازی)

تست‌های یکپارچه‌سازی برای تست کردن تعامل بین کامپوننت‌ها:

```python
def test_create_ticket_api(client, test_user_token):
    """تست API ایجاد تیکت"""
    response = client.post(
        "/api/tickets",
        json={"title": "Test", "description": "Test"},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response.status_code == 201
```

**فایل‌ها:**
- `test_api.py`
- `test_custom_fields_api.py`

### 3. Service Tests (تست‌های سرویس)

تست‌های سرویس برای تست کردن منطق کسب‌وکار:

```python
def test_create_ticket(db, test_user):
    """تست ایجاد تیکت"""
    ticket_data = TicketCreate(...)
    ticket = ticket_service.create_ticket(db, ticket_data, test_user.id)
    assert ticket.id is not None
```

**فایل‌ها:**
- `test_services.py` / `test_services_complete.py`

### 4. Model Tests (تست‌های مدل)

تست‌های مدل برای تست کردن مدل‌های دیتابیس:

```python
def test_user_model(db):
    """تست مدل User"""
    user = User(...)
    db.add(user)
    db.commit()
    assert user.id is not None
```

**فایل‌ها:**
- `test_models.py` / `test_models_complete.py`

---

## نوشتن تست جدید

### 1. ساختار پایه

```python
"""
تست‌های [نام ماژول]
"""
import pytest
from app.models import User
from app.core.enums import UserRole

def test_example(db, test_user):
    """تست مثال"""
    # Arrange (آماده‌سازی)
    # Act (اجرا)
    # Assert (بررسی)
    assert True
```

### 2. استفاده از Fixtures

Fixtures در `conftest.py` تعریف شده‌اند:

```python
def test_my_test(db, test_user, test_ticket):
    """تست با استفاده از fixtures"""
    # db: Session دیتابیس تست
    # test_user: کاربر تست
    # test_ticket: تیکت تست
    pass
```

### 3. Markers

استفاده از markers برای دسته‌بندی تست‌ها:

```python
@pytest.mark.unit
def test_unit_test():
    """تست واحد"""
    pass

@pytest.mark.integration
def test_integration_test():
    """تست یکپارچه‌سازی"""
    pass

@pytest.mark.slow
def test_slow_test():
    """تست کند"""
    pass
```

### 4. Exception Testing

تست کردن استثناها:

```python
def test_division_by_zero():
    """تست تقسیم بر صفر"""
    with pytest.raises(ZeroDivisionError):
        1 / 0
```

### 5. Parametrize

تست با پارامترهای مختلف:

```python
@pytest.mark.parametrize("priority", [
    TicketPriority.LOW,
    TicketPriority.MEDIUM,
    TicketPriority.HIGH,
    TicketPriority.CRITICAL
])
def test_ticket_priority(priority):
    """تست اولویت‌های مختلف"""
    assert priority in TicketPriority
```

---

## Coverage

### هدف Coverage

هدف ما حداقل **70% Coverage** برای کدهای اصلی است.

### مشاهده Coverage

```bash
# اجرای با Coverage
pytest --cov=app --cov-report=html

# مشاهده گزارش
# فایل htmlcov/index.html را باز کنید
```

### بهبود Coverage

1. تست‌های جدید برای بخش‌های بدون Coverage بنویسید
2. Edge cases را تست کنید
3. Error handling را تست کنید

---

## بهترین روش‌ها

### 1. نام‌گذاری

✅ **خوب:**
```python
def test_user_creation_with_valid_data():
    """تست ایجاد کاربر با داده‌های معتبر"""
    pass
```

❌ **بد:**
```python
def test1():
    """تست"""
    pass
```

### 2. ساختار تست

از الگوی **AAA** (Arrange-Act-Assert) استفاده کنید:

```python
def test_example(db):
    # Arrange (آماده‌سازی)
    user_data = UserCreate(...)
    
    # Act (اجرا)
    user = create_user(db, user_data)
    
    # Assert (بررسی)
    assert user.id is not None
    assert user.username == "testuser"
```

### 3. Isolation

هر تست باید مستقل باشد:

```python
# ✅ خوب: استفاده از fixture برای دیتابیس تازه
def test_example(db):
    # هر تست یک دیتابیس تازه دارد
    pass

# ❌ بد: استفاده از دیتابیس مشترک
def test_example():
    # ممکن است با تست‌های دیگر تداخل داشته باشد
    pass
```

### 4. Documentation

همیشه docstring برای تست‌ها بنویسید:

```python
def test_user_creation(db):
    """
    تست ایجاد کاربر با داده‌های معتبر.
    باید کاربر با موفقیت ایجاد شود و تمام فیلدها صحیح باشند.
    """
    pass
```

### 5. Assertions

از assertions واضح استفاده کنید:

```python
# ✅ خوب
assert user.is_active is True
assert len(tickets) == 5

# ❌ بد
assert user.is_active
assert tickets
```

---

## اجرای تست‌ها در CI/CD

### GitHub Actions (مثال)

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

---

## عیب‌یابی

### مشکل: تست‌ها fail می‌شوند

1. بررسی کنید دیتابیس تست درست تنظیم شده باشد
2. بررسی کنید fixtures درست کار می‌کنند
3. بررسی کنید imports درست هستند

### مشکل: Coverage پایین است

1. تست‌های جدید برای بخش‌های بدون Coverage بنویسید
2. Edge cases را تست کنید
3. Error handling را تست کنید

---

## منابع

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Testing Best Practices](https://docs.python-guide.org/writing/tests/)

---

**آخرین به‌روزرسانی:** 2025-01-23  
**نسخه:** 1.0.0

