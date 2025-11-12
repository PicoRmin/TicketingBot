# 🔧 راهنمای سریع رفع مشکل CORS

## ⚡ راه‌حل فوری

### مرحله ۱: بررسی `.env` فایل

مطمئن شوید فایل `.env` در ریشه پروژه وجود دارد و شامل این خط است:

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8000,http://localhost:5173,http://127.0.0.1:5173
```

### مرحله ۲: ری‌استارت Backend

**⚠️ مهم**: بعد از هر تغییر در `.env`، Backend را **حتماً** ری‌استارت کنید:

```powershell
# 1. توقف Backend (Ctrl+C)

# 2. دوباره اجرا کنید
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### مرحله ۳: بررسی لاگ‌ها

بعد از ری‌استارت، در لاگ‌ها باید ببینید:

```
INFO:     CORS allowed origins: ['http://localhost:3000', 'http://localhost:8080', ...]
INFO:     Application startup complete.
```

### مرحله ۴: تست در مرورگر

1. باز کردن: `http://localhost:5173`
2. F12 → Console
3. این دستور را بزنید:

```javascript
fetch('http://127.0.0.1:8000/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

اگر خطای CORS نداد، مشکل حل شده است! ✅

## 🔍 اگر هنوز خطا دارید

### بررسی ۱: Backend در حال اجرا است؟

```powershell
# در PowerShell:
Invoke-WebRequest -Uri "http://127.0.0.1:8000/health"
```

اگر خطا داد، Backend در حال اجرا نیست.

### بررسی ۲: `.env` فایل درست است؟

```powershell
# بررسی محتوای .env
Get-Content .env | Select-String "CORS"
```

باید این خط را ببینید:
```
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:8000,http://localhost:5173,http://127.0.0.1:5173
```

### بررسی ۳: Backend ری‌استارت شده؟

**مهم**: تغییرات `.env` فقط با ری‌استارت Backend اعمال می‌شوند!

### بررسی ۴: لاگ‌های Backend

```powershell
Get-Content logs/app.log -Tail 20 | Select-String "CORS"
```

باید ببینید:
```
CORS allowed origins: ['http://localhost:5173', ...]
```

## 🚨 راه‌حل جایگزین (اگر مشکل حل نشد)

اگر هنوز مشکل دارید، می‌توانید موقتاً CORS را برای همه origins فعال کنید:

**⚠️ فقط برای Development!**

در `app/main.py`:

```python
# Configure CORS - Development only!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ فقط برای development!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**⚠️ هشدار**: این تنظیم فقط برای development است. در production حتماً origins مشخص کنید!

---

**نکته مهم**: همیشه بعد از تغییر `.env`، Backend را ری‌استارت کنید! 🔄

