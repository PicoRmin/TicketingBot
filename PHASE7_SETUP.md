# راهنمای فاز ۷: سیستم دو زبانه / Phase 7: Bilingual System Guide

## ✅ کارهای انجام شده

- ✅ ایجاد سیستم ترجمه (i18n) سبک برای Backend
- ✅ ایجاد فایل‌های ترجمه JSON برای فارسی و انگلیسی: `app/i18n/fa.json`, `app/i18n/en.json`
- ✅ ایجاد ماژول مترجم: `app/i18n/translator.py` با کش و تشخیص ساده Accept-Language
- ⏳ ادغام تدریجی پیام‌های API و خطاها (گام بعدی)

## 📁 ساختار فایل‌ها

```
app/
└── i18n/
    ├── __init__.py
    ├── en.json                  ✅ ترجمه انگلیسی
    ├── fa.json                  ✅ ترجمه فارسی
    └── translator.py            ✅ توابع translate و تشخیص زبان
```

## 🧩 نحوه استفاده در Backend

### ۱) ترجمه یک پیام
```python
from app.i18n.translator import translate
from app.core.enums import Language

msg = translate("auth.login_success", Language.FA)
```

### 2) تشخیص زبان از Accept-Language
```python
from app.i18n.translator import translate, detect_language_from_accept_header

def build_message(request):
    lang = detect_language_from_accept_header(request.headers.get("accept-language"))
    return {"message": translate("common.error", lang)}
```

### 3) اولویت زبان کاربر
- اگر کاربر وارد شده است و مدل User دارای فیلد `language` است، همان را استفاده کنید.
- در غیر این صورت از `Accept-Language` و در نهایت پیش‌فرض فارسی (FA).

نمونه:
```python
def resolve_lang(request, user=None):
    from app.core.enums import Language
    if user and getattr(user, "language", None):
        return Language(user.language)
    from app.i18n.translator import detect_language_from_accept_header
    return detect_language_from_accept_header(request.headers.get("accept-language"))
```

## 🔧 کلیدهای آماده
- `common.*`, `auth.*`, `tickets.*`, `files.*`, `validation.*`
- در صورت نیاز کلیدهای جدید اضافه کنید و در JSONها همسان‌سازی کنید.

## 🧪 تست سریع
1. اجرای API:
   ```bash
   uvicorn app.main:app --reload
   ```
2. درخواست با هدر فارسی (پیش‌فرض):
   ```bash
   curl -s http://localhost:8000/health
   ```
3. درخواست با هدر انگلیسی:
   ```bash
   curl -s http://localhost:8000/health -H "Accept-Language: en"
   ```

## ✅ چک‌لیست فاز ۷
- [x] ایجاد سیستم ترجمه (i18n)
- [x] ایجاد فایل‌های ترجمه (JSON) برای فارسی و انگلیسی
- [x] ایجاد Helper Functions برای ترجمه
- [ ] ترجمه پیام‌های سیستم (ادغام در API)
- [ ] ترجمه پیام‌های خطا
- [ ] ترجمه گزارش‌ها

## 🎯 مراحل بعدی
- استفاده از `translate` در پیام‌های موفق/خطا در Routers (auth, tickets, files)
- یک Middleware کوچک برای resolve زبان و تزریق آن در state درخواست
- پوشش پیام‌ها و گزارش‌ها طبق کلیدهای JSON

---

**تاریخ:** 2025-11-11

