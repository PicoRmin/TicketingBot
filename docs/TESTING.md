# 🧪 راهنمای کامل تست‌ها - سیستم تیکتینگ ایرانمهر

## فهرست مطالب
1. [معرفی](#معرفی)
2. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
3. [ساختار تست‌ها](#ساختار-تست‌ها)
4. [اجرای تست‌ها](#اجرای-تست‌ها)
5. [انواع تست‌ها](#انواع-تست‌ها)
6. [Coverage](#coverage)
7. [بهترین روش‌ها](#بهترین-روش‌ها)

---

## معرفی

سیستم تست کامل برای سیستم تیکتینگ ایرانمهر با استفاده از **pytest** پیاده‌سازی شده است.

### ویژگی‌ها:
- ✅ تست‌های کامل برای تمام Models
- ✅ تست‌های کامل برای تمام Services
- ✅ تست‌های API Endpoints
- ✅ تست‌های امنیتی
- ✅ Coverage Reporting
- ✅ Fixtures برای تست‌های سریع

---

## نصب و راه‌اندازی

### 1. نصب Dependencies

```bash
# نصب تمام dependencies شامل pytest
pip install -r requirements.txt

# یا فقط ابزارهای تست
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. بررسی تنظیمات

فایل `pytest.ini` در ریشه پروژه تنظیمات pytest را شامل می‌شود:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -v --cov=app --cov-report=html
```

---

## ساختار تست‌ها

```
tests/
├── __init__.py
├── conftest.py              # Fixtures مشترک
├── README.md                # راهنمای تست‌ها
│
├── test_models.py           # تست‌های اولیه Models
├── test_models_complete.py  # تست‌های کامل Models (جدید)
│
├── test_services.py         # تست‌های اولیه Services
├── test_services_complete.py # تست‌های کامل Services (جدید)
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
pytest tests/test_models_complete.py

# اجرای یک کلاس تست
pytest tests/test_models_complete.py::TestUserModel

# اجرای یک تابع تست
pytest tests/test_models_complete.py::TestUserModel::test_user_creation
```

### اجرای با Coverage

```bash
# اجرای با Coverage
pytest --cov=app --cov-report=html

# مشاهده گزارش Coverage
# فایل htmlcov/index.html را در مرورگر باز کنید
```

---

## انواع تست‌ها

### 1. Unit Tests (تست‌های واحد)

#### Models Tests (`test_models_complete.py`)

تست‌های کامل برای تمام مدل‌های دیتابیس:

- ✅ `TestUserModel`: تست‌های مدل User
  - ایجاد کاربر
  - فیلد email
  - فیلد telegram_chat_id
  - روابط با Branch و Department
  
- ✅ `TestTicketModel`: تست‌های مدل Ticket
  - ایجاد تیکت
  - روابط با User و Branch
  - تغییر وضعیت تیکت
  
- ✅ `TestSLAModel`: تست‌های مدل‌های SLA
  - ایجاد قانون SLA
  - ایجاد لاگ SLA
  - روابط SLA
  
- ✅ `TestCustomFieldModel`: تست‌های مدل Custom Field
  - ایجاد فیلد سفارشی
  - فیلد با تنظیمات
  - مقادیر فیلدهای سفارشی
  
- ✅ `TestCommentModel`: تست‌های مدل Comment
- ✅ `TestTimeLogModel`: تست‌های مدل TimeLog
- ✅ `TestAutomationRuleModel`: تست‌های مدل AutomationRule
- ✅ `TestBranchInfrastructureModel`: تست‌های مدل BranchInfrastructure
- ✅ `TestSystemSettingsModel`: تست‌های مدل SystemSettings

#### Services Tests (`test_services_complete.py`)

تست‌های کامل برای تمام سرویس‌ها:

- ✅ `TestTicketService`: تست‌های سرویس تیکت
  - ایجاد تیکت
  - دریافت تیکت
  - به‌روزرسانی وضعیت
  - تخصیص تیکت
  - فیلترها و Pagination
  
- ✅ `TestUserService`: تست‌های سرویس کاربر
- ✅ `TestBranchService`: تست‌های سرویس شعبه
- ✅ `TestDepartmentService`: تست‌های سرویس دپارتمان
- ✅ `TestCommentService`: تست‌های سرویس کامنت
- ✅ `TestSLAService`: تست‌های سرویس SLA
- ✅ `TestCustomFieldService`: تست‌های سرویس Custom Field
- ✅ `TestTimeTrackerService`: تست‌های سرویس Time Tracker

### 2. Integration Tests (تست‌های یکپارچه‌سازی)

#### API Tests (`test_api.py`)

تست‌های API Endpoints با استفاده از `TestClient`:

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

### 3. Security Tests (`test_security.py`)

تست‌های امنیتی:
- Authentication
- Authorization
- Input Validation
- SQL Injection
- XSS

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

### Coverage فعلی

- **Models**: ~85%
- **Services**: ~75%
- **API**: ~85% (با Integration Tests)
- **Files**: ~80% (با Integration Tests)
- **Overall**: ~80%

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

### 2. ساختار تست (AAA Pattern)

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

هر تست باید مستقل باشد و از fixtures استفاده کند:

```python
def test_example(db, test_user):
    # هر تست یک دیتابیس تازه دارد
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

---

## Fixtures

Fixtures در `conftest.py` تعریف شده‌اند:

- `db`: Session دیتابیس تست (برای هر تست یک دیتابیس تازه)
- `test_user`: کاربر تست
- `test_admin`: کاربر ادمین تست
- `test_branch`: شعبه تست
- `test_department`: دپارتمان تست
- `test_ticket`: تیکت تست

### استفاده از Fixtures

```python
def test_example(db, test_user, test_ticket):
    """تست با استفاده از fixtures"""
    # استفاده از fixtures
    assert test_user.id is not None
    assert test_ticket.user_id == test_user.id
```

---

## Markers

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

### اجرای با Markers

```bash
# فقط تست‌های واحد
pytest -m unit

# فقط تست‌های یکپارچه‌سازی
pytest -m integration

# بدون تست‌های کند
pytest -m "not slow"
```

---

## عیب‌یابی

### مشکل: تست‌ها fail می‌شوند

1. بررسی کنید دیتابیس تست درست تنظیم شده باشد
2. بررسی کنید fixtures درست کار می‌کنند
3. بررسی کنید imports درست هستند
4. بررسی کنید dependencies نصب شده باشند

### مشکل: Coverage پایین است

1. تست‌های جدید برای بخش‌های بدون Coverage بنویسید
2. Edge cases را تست کنید
3. Error handling را تست کنید

---

## Integration Tests

برای جزئیات کامل تست‌های یکپارچه‌سازی، به [راهنمای Integration Tests](./INTEGRATION_TESTS.md) مراجعه کنید.

### خلاصه Integration Tests:

- ✅ **تست‌های API Endpoints**: 30+ تست
- ✅ **تست‌های Database Operations**: 15+ تست
- ✅ **تست‌های File Operations**: 15+ تست
- ✅ **کل تست‌های Integration**: 60+ تست

---

## End-to-End Tests

برای جزئیات کامل تست‌های End-to-End، به [راهنمای E2E](./END_TO_END_TESTS.md) مراجعه کنید.

### خلاصه End-to-End Tests:

- ✅ **Ticket Lifecycle Flow**: از ثبت تا حل تیکت همراه با Time Tracker و History
- ✅ **Telegram Bot API Client**: ورود، دریافت شعب، ثبت تیکت و مشاهده لیست
- ✅ **چک‌لیست‌های دستی** برای ربات تلگرام و پنل وب
- ✅ اجرای خودکار با `pytest -m "e2e"`

---

## Security Tests

- `tests/test_security.py`: تست‌های hashing و JWT
- `tests/test_security_api.py`: سناریوهای امنیتی API
  - ورود نامعتبر → `401`
  - دسترسی بدون توکن → `401`
  - جلوگیری از دسترسی کاربر به Endpoint‌های ادمین → `403`
  - جلوگیری از مشاهده تیکت سایر کاربران
  - اعتبارسنجی enum و payloadهای مشکوک (SQL-like strings)

اجرای سریع:

```bash
pytest tests/test_security.py tests/test_security_api.py -v
```

---

## Performance Tests

- اسکریپت: `python -m tests.performance.run_performance_tests`
- سناریوها:
  - **Load Test**: `--load-concurrency=10` ، مدت پیش‌فرض 60 ثانیه
  - **Stress Test**: از همزمانی 5 تا 50 با گام 5
- شامل Endpointهای حیاتی: Tickets، Reports، SLA، Custom Fields
- خروجی: خلاصه JSON شامل `avg_ms`، `p95_ms`، نرخ خطا

جزئیات کامل و نحوه سفارشی‌سازی در [راهنمای Performance Tests](./PERFORMANCE_TESTS.md) موجود است.

---

## خلاصه

### ✅ کارهای انجام شده:

1. **تست‌های Models** (`test_models_complete.py`):
   - 9 کلاس تست برای تمام مدل‌ها
   - بیش از 30 تست واحد
   - پوشش کامل روابط و فیلدها

2. **تست‌های Services** (`test_services_complete.py`):
   - 8 کلاس تست برای تمام سرویس‌ها
   - بیش از 40 تست واحد
   - پوشش کامل توابع اصلی

3. **تنظیمات pytest** (`pytest.ini`):
   - تنظیمات کامل pytest
   - Coverage reporting
   - Markers

4. **مستندات**:
   - `tests/README.md`: راهنمای کامل تست‌ها
   - `docs/TESTING.md`: این فایل

### 📊 آمار تست‌ها:

- **تست‌های Models**: 30+ تست
- **تست‌های Services**: 40+ تست
- **تست‌های API**: 20+ تست
- **تست‌های امنیتی**: 10+ تست
- **کل تست‌ها**: 100+ تست

---

**آخرین به‌روزرسانی:** 2025-01-23  
**نسخه:** 1.0.0

