# 🧪 تست و بررسی CORS

## ✅ بررسی‌های انجام شده

1. ✅ `.env` فایل وجود دارد
2. ✅ `CORS_ORIGINS` در `.env` تنظیم شده
3. ✅ Backend در حال اجرا است (health check موفق)

## 🔧 راه‌حل نهایی

### مرحله ۱: ری‌استارت Backend

**⚠️ مهم**: Backend را حتماً ری‌استارت کنید:

```powershell
# در ترمینال Backend:
# 1. توقف (Ctrl+C)
# 2. دوباره اجرا:
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### مرحله ۲: بررسی لاگ‌ها

بعد از ری‌استارت، باید این پیام را ببینید:

```
INFO:     CORS allowed origins: ['http://localhost:5173', 'http://127.0.0.1:5173', ...]
INFO:     Application startup complete.
```

### مرحله ۳: تست در مرورگر

1. باز کردن: `http://localhost:5173`
2. F12 → Console
3. این دستور را بزنید:

```javascript
fetch('http://127.0.0.1:8000/health', {
  method: 'GET',
  headers: {
    'Content-Type': 'application/json'
  }
})
  .then(r => r.json())
  .then(data => {
    console.log('✅ CORS OK:', data);
  })
  .catch(err => {
    console.error('❌ CORS Error:', err);
  });
```

اگر `✅ CORS OK` دیدید، مشکل حل شده است!

## 🔍 اگر هنوز خطا دارید

### بررسی دقیق‌تر:

1. **بررسی Network Tab:**
   - F12 → Network
   - یک درخواست API بزنید
   - روی درخواست کلیک کنید
   - در Headers بررسی کنید:
     - `Access-Control-Allow-Origin` باید `http://localhost:5173` باشد
     - `Access-Control-Allow-Credentials` باید `true` باشد

2. **بررسی لاگ‌های Backend:**
   ```powershell
   Get-Content logs/app.log -Tail 50 | Select-String "CORS"
   ```

3. **تست مستقیم CORS:**
   ```powershell
   $headers = @{
       Origin = "http://localhost:5173"
   }
   Invoke-WebRequest -Uri "http://127.0.0.1:8000/health" -Headers $headers -Method OPTIONS
   ```

---

**نکته**: همیشه بعد از تغییر `.env`، Backend را ری‌استارت کنید! 🔄

