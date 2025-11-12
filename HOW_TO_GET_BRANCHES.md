# راهنمای دریافت لیست branch_id ها

## 📋 روش‌های دریافت لیست شعب

### روش ۱: استفاده از اسکریپت Python

```powershell
python .\scripts\list_branches.py
```

خروجی:
```
============================================================
📋 لیست شعب
============================================================
ID    نام                            کد             وضعیت    
------------------------------------------------------------
1     دفتر مرکزی                    MAIN-001       ✅ فعال   
2     کرج - گلشهر                   KARAJ-001      ✅ فعال   
...
============================================================

📊 مجموع: X شعبه
```

### روش ۲: استفاده از API (Swagger)

1. باز کردن: `http://127.0.0.1:8000/docs`
2. پیدا کردن endpoint: `GET /api/branches`
3. کلیک روی "Try it out"
4. کلیک روی "Execute"
5. مشاهده لیست شعب با `id` و `name`

### روش ۳: استفاده از API (PowerShell)

```powershell
# ابتدا لاگین کنید و token بگیرید
$loginBody = @{
    username = "admin"
    password = "admin123"
} | ConvertTo-Json

$loginResponse = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/auth/login" `
    -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "username=admin&password=admin123"

$token = ($loginResponse.Content | ConvertFrom-Json).access_token

# دریافت لیست شعب
$headers = @{
    Authorization = "Bearer $token"
}

$branches = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/branches" `
    -Headers $headers | ConvertFrom-Json

# نمایش لیست
$branches | Format-Table id, name, code, is_active
```

### روش ۴: استفاده از پنل وب

1. باز کردن: `http://localhost:5173`
2. لاگین با `admin/admin123`
3. رفتن به صفحه "شعب" (Branches)
4. مشاهده لیست کامل شعب با ID ها

## 📝 مثال خروجی API

```json
[
  {
    "id": 1,
    "name": "دفتر مرکزی",
    "name_en": "Main Office",
    "code": "MAIN-001",
    "address": "تهران، خیابان ...",
    "phone": "021-12345678",
    "is_active": true,
    "created_at": "2025-01-01T00:00:00"
  },
  {
    "id": 2,
    "name": "کرج - گلشهر",
    "name_en": null,
    "code": "KARAJ-001",
    "address": null,
    "phone": null,
    "is_active": true,
    "created_at": "2025-01-01T00:00:00"
  }
]
```

## 🔍 استفاده در ایجاد تیکت

برای ایجاد تیکت با یک شعبه خاص:

```json
{
  "title": "مشکل تلفن",
  "description": "تلفن واحد ایکس قطع است",
  "category": "equipment",
  "branch_id": 1
}
```

**نکته**: اگر `branch_id` را `0` یا `null` بفرستید، تیکت بدون شعبه ثبت می‌شود.

---

**آخرین به‌روزرسانی**: 2025-01-12

