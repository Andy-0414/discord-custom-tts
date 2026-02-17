@echo off
echo Stopping Discord Custom TTS Bot...

REM Kill all python processes (Windows)
taskkill /F /IM python.exe /T 2>nul

if %errorlevel% equ 0 (
    echo Bot stopped successfully!
) else (
    echo No bot process found.
)

pause
