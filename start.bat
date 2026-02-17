@echo off
echo Starting Discord Custom TTS Bot...
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate venv and run bot
cd /d "%~dp0"
venv\Scripts\python.exe bot.py

pause
