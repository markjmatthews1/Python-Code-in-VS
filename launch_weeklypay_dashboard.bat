@echo off
echo ========================================
echo  WeeklyPay Dashboard with Fixed P/L
echo ========================================
echo.
echo Starting Streamlit dashboard...
echo Press Ctrl+C to stop the dashboard
echo.

cd weeklypay_rotation_app
streamlit run simple_dashboard.py

pause
