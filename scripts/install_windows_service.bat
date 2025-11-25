@echo off
REM اسکریپت نصب Windows Service برای سیستم تیکتینگ ایرانمهر
REM Install Windows Service script for Iranmehr Ticketing System

setlocal

echo === Windows Service Installation ===
echo.

REM بررسی دسترسی Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] This script must be run as Administrator!
    pause
    exit /b 1
)

REM تنظیمات
set "PROJECT_DIR=%~dp0.."
set "SERVICE_NAME=TicketingService"
set "DISPLAY_NAME=Iranmehr Ticketing System"
set "DESCRIPTION=سیستم تیکتینگ ایرانمهر"

REM بررسی وجود NSSM
where nssm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] NSSM not found!
    echo Please download NSSM from https://nssm.cc/download
    echo and add nssm.exe to your PATH or place it in System32
    pause
    exit /b 1
)

REM بررسی وجود virtual environment
if not exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please create virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    pause
    exit /b 1
)

REM حذف سرویس قبلی (اگر وجود دارد)
nssm stop %SERVICE_NAME% >nul 2>&1
nssm remove %SERVICE_NAME% confirm >nul 2>&1

REM نصب سرویس جدید
echo [INFO] Installing service...
nssm install %SERVICE_NAME% "%PROJECT_DIR%\venv\Scripts\python.exe" "-m uvicorn app.main:app --host 0.0.0.0 --port 8000"

REM تنظیمات سرویس
echo [INFO] Configuring service...
nssm set %SERVICE_NAME% AppDirectory "%PROJECT_DIR%"
nssm set %SERVICE_NAME% DisplayName "%DISPLAY_NAME%"
nssm set %SERVICE_NAME% Description "%DESCRIPTION%"
nssm set %SERVICE_NAME% Start SERVICE_AUTO_START
nssm set %SERVICE_NAME% AppStdout "%PROJECT_DIR%\logs\service.log"
nssm set %SERVICE_NAME% AppStderr "%PROJECT_DIR%\logs\service_error.log"
nssm set %SERVICE_NAME% AppRotateFiles 1
nssm set %SERVICE_NAME% AppRotateOnline 1
nssm set %SERVICE_NAME% AppRotateSeconds 86400
nssm set %SERVICE_NAME% AppRotateBytes 10485760

REM Environment variables
nssm set %SERVICE_NAME% AppEnvironmentExtra "PYTHONUNBUFFERED=1"

REM شروع سرویس
echo [INFO] Starting service...
nssm start %SERVICE_NAME%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [SUCCESS] Service installed and started successfully!
    echo.
    echo Service name: %SERVICE_NAME%
    echo Display name: %DISPLAY_NAME%
    echo.
    echo To manage the service:
    echo   nssm start %SERVICE_NAME%
    echo   nssm stop %SERVICE_NAME%
    echo   nssm restart %SERVICE_NAME%
    echo   nssm status %SERVICE_NAME%
    echo   nssm remove %SERVICE_NAME% confirm
) else (
    echo.
    echo [ERROR] Failed to start service!
    echo Check logs at: %PROJECT_DIR%\logs\service_error.log
)

echo.
pause

endlocal

