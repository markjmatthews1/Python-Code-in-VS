import tkinter as tk
from tkinter import ttk
from datetime import datetime

def create_fixed_popup():
    """Create a popup with GUARANTEED two-column layout using PanedWindow"""
    
    # Create main window
    root = tk.Tk()
    root.title("🎉 Dividend Tracker - Two Columns FIXED!")
    root.geometry("1000x600")
    root.configure(bg="#1e1e2e")
    
    # Main header
    header_frame = tk.Frame(root, bg="#4c956c", height=60)
    header_frame.pack(fill="x", padx=10, pady=10)
    header_frame.pack_propagate(False)
    
    header_label = tk.Label(header_frame, 
                           text="🎉 DIVIDEND TRACKER COMPLETE! 🎉", 
                           font=("Arial", 16, "bold"), 
                           bg="#4c956c", fg="white")
    header_label.pack(expand=True)
    
    # Use PanedWindow for guaranteed two-column layout
    paned_window = tk.PanedWindow(root, orient=tk.HORIZONTAL, 
                                 sashwidth=10, bg="#2d3748", 
                                 sashrelief=tk.RAISED)
    paned_window.pack(fill="both", expand=True, padx=10, pady=10)
    
    # LEFT PANE - DIVIDEND ACCOUNTS
    left_frame = tk.LabelFrame(paned_window, text="💰 DIVIDEND ACCOUNTS", 
                              font=("Arial", 12, "bold"), 
                              bg="#2d3748", fg="#90cdf4", 
                              relief="raised", bd=2)
    paned_window.add(left_frame, minsize=400, width=450)
    
    # Add dividend accounts content
    accounts = [
        ("E*TRADE IRA", 210683.95, 18, 17.2, "#4ade80"),
        ("E*TRADE Taxable", 58545.98, 6, 15.8, "#60a5fa"),
        ("Schwab IRA", 15245.50, 3, 12.5, "#f59e0b"),
        ("Schwab Individual", 8120.75, 1, 18.9, "#ef4444")
    ]
    
    for name, value, positions, yield_pct, color in accounts:
        account_frame = tk.Frame(left_frame, bg="#374151", relief="raised", bd=1)
        account_frame.pack(fill="x", padx=10, pady=5)
        
        # Account header
        header_frame = tk.Frame(account_frame, bg=color, height=30)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"✅ {name}", font=("Arial", 10, "bold"), 
                bg=color, fg="white").pack(side="left", padx=10, pady=5)
        
        # Account details
        details_frame = tk.Frame(account_frame, bg="#374151")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(details_frame, 
                text=f"${value:,.2f}  |  {positions} positions  |  {yield_pct}% yield", 
                font=("Arial", 9), bg="#374151", fg="white").pack(side="left")
    
    # RIGHT PANE - WEEKLY CHANGES
    right_frame = tk.LabelFrame(paned_window, text="📈 WEEKLY PORTFOLIO CHANGES", 
                               font=("Arial", 12, "bold"), 
                               bg="#374151", fg="#90cdf4", 
                               relief="raised", bd=2)
    paned_window.add(right_frame, minsize=400, width=450)
    
    # Add weekly changes content
    weekly_changes = [
        ("E*TRADE IRA", 208156.42, 210683.95, 2527.53, 1.21),
        ("E*TRADE Taxable", 57891.22, 58545.98, 654.76, 1.13), 
        ("Schwab IRA", 15089.15, 15245.50, 156.35, 1.04),
        ("Schwab Individual", 7995.80, 8120.75, 124.95, 1.56)
    ]
    
    # Header
    tk.Label(right_frame, text="Account Performance This Week:", 
            font=("Arial", 11, "bold"), bg="#374151", fg="#90cdf4").pack(pady=10)
    
    total_last_week = 0
    total_current_week = 0
    
    for account, last_week, current_week, change_dollars, change_percent in weekly_changes:
        total_last_week += last_week
        total_current_week += current_week
        
        # Determine change color
        change_color = "#4ade80" if change_dollars > 0 else "#ef4444"
        change_symbol = "+" if change_dollars > 0 else ""
        
        # Create change row
        change_frame = tk.Frame(right_frame, bg="#4a5568", relief="raised", bd=1)
        change_frame.pack(fill="x", padx=10, pady=3)
        
        # Account name
        tk.Label(change_frame, text=account, font=("Arial", 10, "bold"), 
                bg="#4a5568", fg="#ffffff").pack(side="left", padx=10, pady=5)
        
        # Change percentage
        tk.Label(change_frame, text=f"{change_symbol}{change_percent:.1f}%", 
                font=("Arial", 10, "bold"), 
                bg="#4a5568", fg=change_color).pack(side="right", padx=10, pady=5)
        
        # Change amount
        tk.Label(change_frame, text=f"{change_symbol}${change_dollars:,.2f}", 
                font=("Arial", 9), 
                bg="#4a5568", fg=change_color).pack(side="right", padx=5, pady=5)
    
    # Total change
    total_change = total_current_week - total_last_week
    total_change_percent = (total_change / total_last_week * 100) if total_last_week > 0 else 0
    total_color = "#4ade80" if total_change > 0 else "#ef4444"
    total_symbol = "+" if total_change > 0 else ""
    
    total_frame = tk.Frame(right_frame, bg="#1f2937", relief="raised", bd=2)
    total_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(total_frame, text="TOTAL PORTFOLIO", font=("Arial", 11, "bold"), 
            bg="#1f2937", fg="#fbbf24").pack(side="left", padx=10, pady=8)
    
    tk.Label(total_frame, text=f"{total_symbol}{total_change_percent:.1f}%", 
            font=("Arial", 11, "bold"), 
            bg="#1f2937", fg=total_color).pack(side="right", padx=10, pady=8)
    
    tk.Label(total_frame, text=f"{total_symbol}${total_change:,.2f}", 
            font=("Arial", 10), 
            bg="#1f2937", fg=total_color).pack(side="right", padx=5, pady=8)
    
    # Close button
    close_btn = tk.Button(root, text="✅ Close", font=("Arial", 12, "bold"), 
                         bg="#4ade80", fg="white", width=12, height=1,
                         command=root.destroy)
    close_btn.pack(pady=10)
    
    # Show the window
    root.mainloop()

if __name__ == "__main__":
    print("🎯 Creating FIXED two-column popup with PanedWindow...")
    create_fixed_popup()
