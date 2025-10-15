@echo off
cd "c:\Users\mjmat\Python Code in VS\weeklypay_rotation_app"
python -m streamlit run simple_dashboard.py --server.port 8502 --browser.gatherUsageStats false
pause