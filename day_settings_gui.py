import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"dashboard_interval": 1}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

# ...existing code...
DEFAULT_SETTINGS = {"dashboard_interval": 1, "volatility_lookback_bars": 12}
# ...existing code...

class SettingsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Dashboard Setup")
        self.root.configure(bg="#222244")
        self.settings = load_settings()

        tk.Label(root, text="Dashboard Refresh Interval:", font=("Arial", 14, "bold"), fg="#fff", bg="#222244").pack(pady=(20,10))
        self.interval_var = tk.IntVar(value=self.settings.get("dashboard_interval", 1))
        interval_frame = tk.Frame(root, bg="#222244")
        interval_frame.pack(pady=5)
        for val, label in [(1, "1 Minute"), (5, "5 Minutes"), (10, "10 Minutes")]:
            ttk.Radiobutton(
                interval_frame, text=label, variable=self.interval_var, value=val
            ).pack(side="left", padx=10)

        # Add more settings here as needed

        # --- New: Volatility Lookback Bars Setting ---
        tk.Label(root, text="Volatility Lookback Bars:", font=("Arial", 14, "bold"), fg="#fff", bg="#222244").pack(pady=(20,10))
        self.volatility_bars_var = tk.IntVar(value=self.settings.get("volatility_lookback_bars", 12))
        bars_frame = tk.Frame(root, bg="#222244")
        bars_frame.pack(pady=5)
        self.bars_entry = ttk.Entry(bars_frame, textvariable=self.volatility_bars_var, width=10)
        self.bars_entry.pack(side="left", padx=10)
        tk.Label(bars_frame, text="bars", font=("Arial", 12), fg="#fff", bg="#222244").pack(side="left")

        tk.Button(
            root, text="Save", font=("Arial", 12, "bold"), bg="#3572b0", fg="#fff",
            activebackground="#285a8c", activeforeground="#fff",
            command=self.save
        ).pack(pady=(20,10))

        self.status_label = tk.Label(root, text="", fg="#4CAF50", bg="#222244", font=("Arial", 12, "italic"))
        self.status_label.pack()

    def save(self):
        self.settings["dashboard_interval"] = self.interval_var.get()
        # --- New: Save Volatility Lookback Bars ---
        self.settings["volatility_lookback_bars"] = self.volatility_bars_var.get()
        save_settings(self.settings)
        self.status_label.config(text="Settings saved!")

def show_settings_gui():
    root = tk.Tk()
    SettingsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    show_settings_gui()