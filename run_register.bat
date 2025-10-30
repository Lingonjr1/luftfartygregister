@echo off
cd /d "%~dp0"
title Running Aircraft Register Scraper

echo ==============================================
echo   Swedish Aircraft Register - Scanner
echo ==============================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3 from https://www.python.org/downloads/
    pause
    exit /b
)

:: Check for venv
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate

:: Upgrade pip silently
python -m pip install --upgrade pip --quiet

:: Install required dependencies
echo Installing dependencies (this may take a moment)...
pip install --quiet requests-futures beautifulsoup4 pandas lxml

:: Run the Python script
echo.
echo Running the scraper...
python scrape_ts_register.py

echo.
echo ==============================================
echo Task complete! Check your output files.
echo ==============================================
pause
