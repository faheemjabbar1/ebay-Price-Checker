@echo off
echo ================================================
echo eBay Price Scraper - Setup Script
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b
)

echo Step 1: Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment!
    pause
    exit /b
)
echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment!
    pause
    exit /b
)
echo Virtual environment activated!
echo.

echo Step 3: Upgrading pip...
python -m pip install --upgrade pip
echo.

echo Step 4: Installing Playwright...
pip install playwright
if errorlevel 1 (
    echo Error: Failed to install Playwright!
    pause
    exit /b
)
echo Playwright installed successfully!
echo.

echo Step 5: Installing Chromium browser...
playwright install chromium
if errorlevel 1 (
    echo Error: Failed to install Chromium!
    pause
    exit /b
)
echo Chromium installed successfully!
echo.

echo ================================================
echo Setup completed successfully!
echo ================================================
echo.
echo You can now run the GUI by double-clicking run_gui.bat
echo or run the command-line version with: python scraper.py
echo.

pause
