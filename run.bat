@echo off
REM CMS Application Launcher Script for Windows

cd /d "%~dp0"

REM Check if venv exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install/update dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet

REM Run application
echo.
echo ==========================================
echo 🚀 Starting CMS Application...
echo ==========================================
echo.
echo 📱 Open your browser:
echo    http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ==========================================
echo.

cd app
python app.py
