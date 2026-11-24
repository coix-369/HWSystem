@echo off
echo Starting Flask Backend...
echo.

REM Activate virtual environment with absolute path
call D:\HWSystem\venv\Scripts\activate.bat

echo Virtual environment activated
echo.

REM Change to flask_backend directory
cd /d D:\HWSystem\flask_backend

REM Start Flask
python run.py
