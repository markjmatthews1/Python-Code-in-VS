import tkinter as tk
import subprocess
import os
import sys
from tkinter import messagebox

# Path to DividendTrackerApp
DIVIDEND_TRACKER_PATH = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
PRICE_TRACKER_PATH = r"c:\Users\mjmat\Python Code in VS\price_tracker"
CATALYST_SCANNER_PATH = r"c:\Users\mjmat\Python Code in VS\catalyst_scanner"
VENV_PYTHON = sys.executable  # Uses your virtual environment or system Python

# Launch function with working directory override
def run_app(command, cwd=None, new_terminal=False):
    if new_terminal:
        # Build the command string for Windows new terminal
        cmd_str = ' '.join(f'"{arg}"' if ' ' in str(arg) else str(arg) for arg in command)
        subprocess.Popen(f'start cmd /k {cmd_str}', cwd=cwd if cwd else os.getcwd(), shell=True)
    else:
        subprocess.Popen(command, cwd=cwd if cwd else os.getcwd())

def launch_catalyst_scanner():
    """Launch Catalyst Scanner in separate terminal for background operation"""
    try:
        # Use absolute paths to avoid directory issues
        script_path = os.path.join(CATALYST_SCANNER_PATH, "catalyst_scanner.py")
        
        # Verify the script exists before trying to run it
        if not os.path.exists(script_path):
            error_msg = f"Script not found at: {script_path}"
            messagebox.showerror("Launch Error", error_msg)
            print(error_msg)
            return
        
        # Use a much simpler approach with cwd parameter
        subprocess.Popen([
            sys.executable, "catalyst_scanner.py"
        ], cwd=CATALYST_SCANNER_PATH, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print(f"Catalyst Scanner launched from: {script_path}")
        
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch Catalyst Scanner: {str(e)}")
        print(f"Error launching Catalyst Scanner: {str(e)}")

def launch_weeklypay_dashboard():
    """Launch WeeklyPay™ Rotation Dashboard"""
    try:
        # Path to WeeklyPay rotation app batch file
        batch_file_path = r"c:\Users\mjmat\Python Code in VS\weeklypay_rotation_app\launch_dashboard.bat"
        
        # Verify the batch file exists before trying to run it
        if not os.path.exists(batch_file_path):
            error_msg = f"WeeklyPay™ dashboard launcher not found at: {batch_file_path}"
            messagebox.showerror("Launch Error", error_msg)
            print(error_msg)
            return
        
        # First check if Streamlit is available
        try:
            import streamlit
            print(f"Streamlit version: {streamlit.__version__}")
        except ImportError:
            error_msg = "Streamlit is not installed. Please install it with: pip install streamlit"
            messagebox.showerror("Missing Dependency", error_msg)
            print(error_msg)
            return
        
        # Launch WeeklyPay™ dashboard using batch file for reliable execution
        process = subprocess.Popen(
            [batch_file_path], 
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print(f"WeeklyPay™ Dashboard launched using batch file: {batch_file_path}")
        print(f"Process ID: {process.pid}")
        messagebox.showinfo("Launch Success", "WeeklyPay™ Dashboard is starting...\n\nPlease wait 10-15 seconds, then access at:\nhttp://localhost:8502")
        
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch WeeklyPay™ Dashboard: {str(e)}")
        print(f"Error launching WeeklyPay™ Dashboard: {str(e)}")

def launch_recovery_app():
    """Launch RecoveryApp™ - Underwater Position Recovery Tool"""
    try:
        # Path to RecoveryApp
        recovery_app_path = r"c:\Users\mjmat\Python Code in VS\RecoveryApp"
        script_path = os.path.join(recovery_app_path, "app.py")
        
        # Verify the script exists before trying to run it
        if not os.path.exists(script_path):
            error_msg = f"RecoveryApp not found at: {script_path}"
            messagebox.showerror("Launch Error", error_msg)
            print(error_msg)
            return
        
        # Launch RecoveryApp in a new console window
        subprocess.Popen([
            sys.executable, "app.py"
        ], cwd=recovery_app_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        print(f"RecoveryApp™ launched from: {script_path}")
        messagebox.showinfo("Launch Success", "RecoveryApp™ - Underwater Position Recovery Tool is starting...\n\nThe application will open in a new window.")
        
    except Exception as e:
        messagebox.showerror("Launch Error", f"Failed to launch RecoveryApp™: {str(e)}")
        print(f"Error launching RecoveryApp™: {str(e)}")

# Define apps and commands
APPS = [
    # --- Dividend Tools ---
    {
        "label": "🚀 Complete Portfolio/Dividend Update",
        "command": [VENV_PYTHON, "proper_excel_updater.py"],
        "cwd": DIVIDEND_TRACKER_PATH,
        "bg": "#4CAF50"
    },
    {
        "label": "💰 Item Price Tracker",
        "command": [VENV_PYTHON, "pt.py"],
        "cwd": PRICE_TRACKER_PATH,
        "bg": "#FF9800"
    },
    {
        "label": "Update Dividend Sheet",
        "command": [VENV_PYTHON, "Update_dividend_sheet.py"],
        "bg": "#2196F3"
    },
    {
        "label": "Wishlist Tracker Dashboard",
        "command": [VENV_PYTHON, os.path.join("wishlist_tracker", "gui", "dashboard_gui.py")],
        "cwd": os.getcwd(),
        "bg": "#9C27B0",
        "new_terminal": True
    },
    {
        "label": "🚀 Enhanced Day Trading System v2.0",
        "command": [VENV_PYTHON, "main_trader.py"],
        "cwd": os.path.join(os.getcwd(), "enhanced_day_trader"),
        "bg": "#FF9800",
        "new_terminal": True
    },
    {
        "label": "View Dividend Screener",
        "command": [VENV_PYTHON, "screen_dividends.py"],
        "bg": "#00BCD4"
    },

    # --- Trading Tools ---
    {
        "label": "Run Dashboard (day.py)",
        "command": [VENV_PYTHON, "day.py"],
        "bg": "#4CAF50",
        "new_terminal": True
    },
    {
        "label": "Market Quote",
        "command": [VENV_PYTHON, "Get_quote.py"],
        "bg": "#FF9800"
    },
    {
        "label": "🏆 WeeklyPay™ Rotation Dashboard",
        "command": launch_weeklypay_dashboard,
        "bg": "#9C27B0"
    },
    {
        "label": "Trade Tracker",
        "command": [VENV_PYTHON, "TradeTracker.py"],
        "bg": "#00BCD4"
    },
    {
        "label": "SSO SDS Trade Strategy",
        "command": [VENV_PYTHON, "SSO_SDS_Trade_Strategy.py"],
        "bg": "#4CAF50"
    },
    {
        "label": "📈 RecoveryApp - Trade Recovery System",
        "command": launch_recovery_app,
        "bg": "#FF9800"
    },

    # --- Catalyst & Analysis Tools ---
    {
        "label": "🔍 Catalyst Scanner (Investment Intelligence)",
        "command": launch_catalyst_scanner,
        "bg": "#E91E63",
        "new_terminal": True
    }
]

# ------------------- GUI Setup -------------------
root = tk.Tk()
root.title("Trading Application Menu")
root.geometry("420x900")
root.configure(bg="#222244")

title = tk.Label(
    root,
    text="Trading Application Menu",
    font=("Arial", 18, "bold"),
    fg="white",
    bg="#222244"
)
title.pack(pady=20)

# Generate buttons dynamically
for app in APPS:
    # Handle different command types
    if callable(app["command"]) and app["label"] == "🔍 Catalyst Scanner (Investment Intelligence)":
        # Special handling for Catalyst Scanner
        btn = tk.Button(
            root,
            text=app["label"],
            font=("Arial", 14),
            bg=app["bg"],
            fg="white",
            command=app["command"]
        )
    elif callable(app["command"]):
        # Regular callable command
        btn = tk.Button(
            root,
            text=app["label"],
            font=("Arial", 14),
            bg=app["bg"],
            fg="white",
            command=app["command"]
        )
    else:
        # List command (subprocess)
        btn = tk.Button(
            root,
            text=app["label"],
            font=("Arial", 14),
            bg=app["bg"],
            fg="white",
            command=lambda cmd=app["command"], cwd=app.get("cwd"), new_term=app.get("new_terminal", False): run_app(cmd, cwd, new_term)
        )
    btn.pack(pady=10, fill="x", padx=40)

# Exit button
btn_exit = tk.Button(
    root,
    text="Exit",
    font=("Arial", 14),
    bg="#F44336",
    fg="white",
    command=root.destroy
)
btn_exit.pack(pady=10, fill="x", padx=40)

root.mainloop()