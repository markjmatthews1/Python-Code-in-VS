@echo off
echo ==========================================
echo    Dividend Tracker App - Starting...
echo ==========================================
echo.

REM Change to the project directory
cd /d "C:\Python_Projects\DividendTrackerApp"

REM Run the dividend tracker
python -m modules.build_dividends_sheet

echo.
echo ==========================================
echo    Processing Complete!
echo ==========================================
pause