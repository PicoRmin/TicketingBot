# 🔧 رفع مشکل ثبت تیکت از طریق Telegram Bot

## 🔴 مشکل

تیکت از طریق بات ثبت نمی‌شد و خطا می‌داد.

## ✅ تغییرات انجام شده

### 1. بهبود Loading User Relationship

در `app/api/tickets.py`:
- استفاده از `joinedload` برای لود کردن user relationship
- اضافه کردن fallback برای زمانی که user لود نمی‌شود
- بهبود error handling

### 2. بررسی کدهای مرتبط

- ✅ `app/telegram_bot/handlers/ticket.py` - درست کار می‌کند
- ✅ `app/telegram_bot/api_client.py` - درست کار می‌کند
- ✅ `app/services/ticket_service.py` - درست کار می‌کند
- ✅ `app/models/ticket.py` - درست تعریف شده
- ✅ `app/schemas/ticket.py` - درست تعریف شده

## 🧪 تست

برای تست:

1. **Backend را ری‌استارت کنید:**
   ```powershell
   uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Telegram Bot را اجرا کنید:**
   ```powershell
   python -m app.telegram_bot.run
   ```

3. **در Telegram:**
   - `/start`
   - `/login` (با username و password)
   - `/newticket` یا از منوی اصلی
   - عنوان تیکت را وارد کنید
   - توضیحات را وارد کنید (حداقل 10 کاراکتر)
   - شعبه را انتخاب کنید (یا skip)
   - دسته‌بندی را انتخاب کنید

## 📋 بررسی لاگ‌ها

بعد از ثبت تیکت، در لاگ‌های Backend باید ببینید:

```
INFO: Creating ticket: title=..., category=..., branch_id=..., user_id=...
DEBUG: Ticket created: id=..., ticket_number=...
INFO: Ticket created successfully: id=..., ticket_number=..., user=...
```

اگر خطایی دیدید، لاگ‌ها را بررسی کنید.

## 🔍 عیب‌یابی

اگر هنوز مشکل دارید:

1. **بررسی لاگ‌های Backend:**
   ```powershell
   Get-Content logs/app.log -Tail 50
   ```

2. **بررسی لاگ‌های Bot:**
   - اگر bot را جداگانه اجرا می‌کنید، لاگ‌ها را در console ببینید

3. **تست مستقیم API:**
   ```powershell
   # Login
   $token = (Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/auth/login" -Method POST -Body @{username="admin";password="admin"} -ContentType "application/x-www-form-urlencoded").Content | ConvertFrom-Json | Select-Object -ExpandProperty access_token
   
   # Create ticket
   $body = @{
       title = "تست تیکت"
       description = "این یک تیکت تست است"
       category = "internet"
   } | ConvertTo-Json
   
   Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/tickets" -Method POST -Headers @{Authorization="Bearer $token"} -Body $body -ContentType "application/json"
   ```

---

**نکته**: همیشه بعد از تغییر کد، Backend را ری‌استارت کنید! 🔄

