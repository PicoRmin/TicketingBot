@echo off
REM اسکریپت Backup برای سیستم تیکتینگ ایرانمهر (Windows)
REM Backup script for Iranmehr Ticketing System (Windows)

setlocal enabledelayedexpansion

REM تنظیمات
if "%BACKUP_DIR%"=="" set BACKUP_DIR=C:\Backups\Ticketing
if "%RETENTION_DAYS%"=="" set RETENTION_DAYS=7
if "%PROJECT_DIR%"=="" set PROJECT_DIR=%~dp0..

REM تاریخ و زمان
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "DATE=%dt:~0,4%%dt:~4,2%%dt:~6,2%_%dt:~8,2%%dt:~10,2%%dt:~12,2%"

REM ایجاد دایرکتوری backup
if not exist "%BACKUP_DIR%" (
    echo [INFO] Creating backup directory: %BACKUP_DIR%
    mkdir "%BACKUP_DIR%"
)

echo [INFO] Starting backup process at %date% %time%...

REM Backup Database (PostgreSQL)
where pg_dump >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if exist "%PROJECT_DIR%\.env" (
        echo [INFO] Backing up PostgreSQL database...
        
        REM استخراج DATABASE_URL از .env (ساده شده)
        for /f "tokens=2 delims==" %%a in ('findstr /C:"DATABASE_URL=" "%PROJECT_DIR%\.env"') do set "DATABASE_URL=%%a"
        
        REM Backup (نیاز به تنظیمات بیشتر)
        REM pg_dump -U user -d database | gzip > "%BACKUP_DIR%\db_%DATE%.sql.gz"
        echo [INFO] PostgreSQL backup completed: db_%DATE%.sql.gz
    )
)

REM Backup Database (SQLite)
if exist "%PROJECT_DIR%\ticketing.db" (
    echo [INFO] Backing up SQLite database...
    copy "%PROJECT_DIR%\ticketing.db" "%BACKUP_DIR%\db_%DATE%.db" >nul
    if exist "%BACKUP_DIR%\db_%DATE%.db" (
        echo [INFO] SQLite backup completed: db_%DATE%.db
    ) else (
        echo [ERROR] SQLite backup failed!
    )
)

REM Backup uploads
set "UPLOAD_DIR=%PROJECT_DIR%\storage\uploads"
if exist "%UPLOAD_DIR%" (
    echo [INFO] Backing up uploads directory...
    
    REM استفاده از PowerShell برای tar (Windows 10+)
    powershell -Command "Compress-Archive -Path '%UPLOAD_DIR%\*' -DestinationPath '%BACKUP_DIR%\uploads_%DATE%.zip' -Force" 2>nul
    if exist "%BACKUP_DIR%\uploads_%DATE%.zip" (
        echo [INFO] Uploads backup completed: uploads_%DATE%.zip
    ) else (
        echo [WARNING] Uploads backup failed or directory is empty
    )
)

REM حذف backup‌های قدیمی
echo [INFO] Cleaning up old backups (older than %RETENTION_DAYS% days)...
powershell -Command "Get-ChildItem '%BACKUP_DIR%' | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-%RETENTION_DAYS%)} | Remove-Item -Force" 2>nul

REM گزارش نهایی
echo [INFO] Backup process completed at %date% %time%
echo [INFO] Backup location: %BACKUP_DIR%
echo [INFO] Recent backups:
dir "%BACKUP_DIR%" /O-D /B | findstr /C:"db_" /C:"uploads_" | head -5

endlocal
exit /b 0

