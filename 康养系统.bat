@echo off
title Bay Area Wellness Tourism System - Auto Start

echo ========================================
echo   Bay Area Wellness Tourism System
echo   One-Click Startup
echo ========================================
echo.

echo [1/2] Starting backend service...
start "Flask Backend" cmd /k "cd /d D:\HWSystem\flask_backend && call D:\HWSystem\venv\Scripts\activate.bat && python run.py"

timeout /t 3 /nobreak >nul

echo [2/2] Starting frontend service...
start "Vue Frontend" cmd /k "cd /d D:\HWSystem\vue_frontend && npm run serve"

echo.
echo ========================================
echo   System started successfully!
echo ========================================
echo.
echo Backend: http://127.0.0.1:5000
echo Frontend: http://localhost:8080
echo.
echo Please wait a few seconds for services to start...
echo Browser will open automatically.
echo.

timeout /t 8 /nobreak >nul

start http://localhost:8080

echo Browser opened. Enjoy!
echo.
pause
