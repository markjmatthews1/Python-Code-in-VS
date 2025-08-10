def show_splash():
    root = tk.Tk()
    root.withdraw()  # Hide the main root window for now
    splash = tk.Toplevel(root)
    splash.title("Loading Trade Tracker...")
    splash.geometry("350x120")
    splash.configure(bg="#23eff2")  # Light blue background
    splash.attributes("-topmost", True)  # Always on top
    label = tk.Label(
        splash,
        text="Loading Trade Tracker...\nPlease wait...",
        font=("Segoe UI", 16, "bold"),
        fg="#0a2463",  # Deep blue text for high contrast
        bg="#b3e0ff",
        pady=30
    )
    label.pack(expand=True, fill="both")
    splash.update()
    return root, splash

def start_main_app(splash):
    root, splash_window = splash
    root.deiconify()
    splash_window.destroy()
    app = TradeTrackerApp(root)
    root.mainloop()

if __name__ == "__main__":
    splash = show_splash()
    # Start the main app after a short delay to ensure splash is visible
    splash[1].after(300, lambda: start_main_app(splash))
    splash[0].mainloop()
