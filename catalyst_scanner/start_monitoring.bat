@echo off
echo =====================================================
echo    Catalyst Scanner Background Monitoring Service
echo =====================================================
echo.

cd /d "%~dp0"

echo Starting monitoring service...
python start_monitoring.py

pause