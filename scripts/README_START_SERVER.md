# راهنمای راه‌اندازی سرور

## روش 1: استفاده از اسکریپت PowerShell

```powershell
# اگر Execution Policy خطا داد، ابتدا این دستور را اجرا کنید:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# سپس اسکریپت را اجرا کنید:
.\scripts\start_server.ps1
```

## روش 2: اجرای مستقیم (بدون اسکریپت)

```powershell
# فعال کردن محیط مجازی (اگر از venv استفاده می‌کنید)
.\.venv\Scripts\Activate.ps1

# راه‌اندازی سرور
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## روش 3: استفاده از Python مستقیم

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## بررسی وضعیت سرور

برای بررسی اینکه سرور در حال اجرا است:

```powershell
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

## متوقف کردن سرور

در ترمینالی که سرور را اجرا کرده‌اید، `Ctrl+C` بزنید.

## لاگ‌ها

لاگ‌های سرور در فایل `logs/app.log` ذخیره می‌شوند.

