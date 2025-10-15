"""
Fix for AlertsPanel layout issue where Add Alert section becomes invisible
"""
import tkinter as tk
from tkinter import ttk

def test_layout_fix():
    """Test the layout fix for AlertsPanel"""
    
    root = tk.Tk()
    root.title("AlertsPanel Layout Test")
    root.geometry("1000x700")
    
    # Create a canvas and scrollbar for scrollable content
    canvas = tk.Canvas(root, bg='lightgray')
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='lightgray')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Test content similar to AlertsPanel structure
    # Header
    header = tk.Frame(scrollable_frame, bg='darkblue', height=60)
    header.pack(fill=tk.X, pady=(0, 10))
    tk.Label(header, text="🚨 Strategy Alerts Monitor", fg='white', bg='darkblue', font=('Arial', 16, 'bold')).pack(pady=10)
    
    # Control Panel
    control = tk.Frame(scrollable_frame, bg='blue', height=80)
    control.pack(fill=tk.X, pady=(0, 10))
    tk.Label(control, text="Control Panel", fg='white', bg='blue', font=('Arial', 12, 'bold')).pack(pady=10)
    
    # Alerts List - LIMITED HEIGHT instead of expand=True
    alerts_frame = tk.Frame(scrollable_frame, bg='green')
    alerts_frame.pack(fill=tk.X, pady=(0, 10))
    tk.Label(alerts_frame, text="Active Alerts", fg='white', bg='green', font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Create a treeview with fixed height
    tree = ttk.Treeview(alerts_frame, height=6)  # Fixed height instead of expand=True
    tree.pack(fill=tk.X, padx=10, pady=5)
    
    # Alert Log - FIXED HEIGHT
    log_frame = tk.Frame(scrollable_frame, bg='orange')
    log_frame.pack(fill=tk.X, pady=(0, 10))
    tk.Label(log_frame, text="Alert Log", fg='white', bg='orange', font=('Arial', 12, 'bold')).pack(pady=5)
    
    log_text = tk.Text(log_frame, height=4, bg='lightyellow')  # Fixed height
    log_text.pack(fill=tk.X, padx=10, pady=5)
    
    # Add Alert Section - THIS SHOULD NOW BE VISIBLE
    add_frame = tk.Frame(scrollable_frame, bg='red')
    add_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(add_frame, text="Add New Alert:", fg='white', bg='red', font=('Arial', 12, 'bold')).pack(pady=5)
    
    # Form elements
    form = tk.Frame(add_frame, bg='red')
    form.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(form, text="Ticker:", bg='red', fg='white').pack(side=tk.LEFT)
    tk.Entry(form, width=10).pack(side=tk.LEFT, padx=5)
    
    tk.Label(form, text="Strategy:", bg='red', fg='white').pack(side=tk.LEFT, padx=(20,0))
    tk.Entry(form, width=15).pack(side=tk.LEFT, padx=5)
    
    # Add Alert Button
    button_frame = tk.Frame(add_frame, bg='red')
    button_frame.pack(fill=tk.X, padx=10, pady=5)
    
    add_button = tk.Button(button_frame, text="➕ Add Alert", bg='darkred', fg='white', font=('Arial', 10, 'bold'))
    add_button.pack(side=tk.LEFT)
    
    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    root.mainloop()

if __name__ == "__main__":
    test_layout_fix()