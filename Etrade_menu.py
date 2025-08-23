import tkinter as tk
import subprocess
import os
import sys

# Path to DividendTrackerApp
DIVIDEND_TRACKER_PATH = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
VENV_PYTHON = sys.executable  # Uses your virtual environment or system Python

# Launch function with working directory override
def run_app(command, cwd=None):
    subprocess.Popen(command, cwd=cwd if cwd else os.getcwd())

# Define apps and commands
APPS = [
    # --- Dividend Tools ---
    {
        "label": "🚀 Complete System Update (Weekend)",
        "command": [VENV_PYTHON, "complete_system_update.py"],
        "cwd": DIVIDEND_TRACKER_PATH,
        "bg": "#4CAF50"
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
        "bg": "#1976D2"
    },
    {
        "label": "Update Ticker Analysis",
        "command": [VENV_PYTHON, "create_historical_ticker_analysis.py"],
        "cwd": DIVIDEND_TRACKER_PATH,
        "bg": "#FF9800"
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
        "bg": "#4CAF50"
    },
    {
        "label": "Market Quote",
        "command": [VENV_PYTHON, "Get_quote.py"],
        "bg": "#FF9800"
    },
    {
        "label": "E*TRADE Account Data",
        "command": [VENV_PYTHON, "Etrade_account_data.py"],
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
        "bg": "#00BCD4"
    },

    # --- Placeholder ---
    {
        "label": "(Future App)",
        "command": lambda: None,
        "bg": "#607D8B"
    }
]

# ------------------- GUI Setup -------------------
root = tk.Tk()
root.title("Trading Application Menu")
root.geometry("420x700")
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
    btn = tk.Button(
        root,
        text=app["label"],
        font=("Arial", 14),
        bg=app["bg"],
        fg="white",
        command=lambda cmd=app["command"], cwd=app.get("cwd"): run_app(cmd, cwd)
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