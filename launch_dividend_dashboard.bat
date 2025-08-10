@echo off
echo.
echo ========================================
echo   DIVIDEND PORTFOLIO DASHBOARD LAUNCHER
echo ========================================
echo.
echo Choose your dashboard:
echo.
echo 1. Command-line Dashboard (Quick Summary)
echo 2. Web Dashboard (Interactive Charts)
echo 3. Both Dashboards
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto command_line
if "%choice%"=="2" goto web_dashboard
if "%choice%"=="3" goto both_dashboards
if "%choice%"=="4" goto exit

:command_line
echo.
echo Starting Command-line Dashboard...
cd "C:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
python portfolio_summary_report.py
pause
goto end

:web_dashboard
echo.
echo Starting Web Dashboard...
echo Dashboard will be available at: http://127.0.0.1:8051
cd "C:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
start python simple_dividend_dashboard.py
timeout /t 3 >nul
start http://127.0.0.1:8051
goto end

:both_dashboards
echo.
echo Starting Both Dashboards...
cd "C:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
echo.
echo === COMMAND-LINE DASHBOARD ===
python portfolio_summary_report.py
echo.
echo === WEB DASHBOARD ===
echo Web dashboard starting at: http://127.0.0.1:8051
start python simple_dividend_dashboard.py
timeout /t 3 >nul
start http://127.0.0.1:8051
goto end

:exit
echo Goodbye!
goto end

:end
echo.
echo Dashboard launcher finished.
pause
