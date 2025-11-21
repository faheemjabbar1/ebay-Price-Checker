@echo off
echo Starting eBay Price Scraper GUI...
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found!
    echo Please run setup.bat first to create the virtual environment.
    pause
    exit /b
)

REM Run the GUI
python gui.py

pause
