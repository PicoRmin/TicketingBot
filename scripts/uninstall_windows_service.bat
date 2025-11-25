@echo off
REM اسکریپت حذف Windows Service
REM Uninstall Windows Service script

setlocal

echo === Windows Service Uninstallation ===
echo.

REM بررسی دسترسی Administrator
net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] This script must be run as Administrator!
    pause
    exit /b 1
)

set "SERVICE_NAME=TicketingService"

REM توقف سرویس
echo [INFO] Stopping service...
nssm stop %SERVICE_NAME%

REM حذف سرویس
echo [INFO] Removing service...
nssm remove %SERVICE_NAME% confirm

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Service removed successfully!
) else (
    echo [ERROR] Failed to remove service!
)

echo.
pause

endlocal

