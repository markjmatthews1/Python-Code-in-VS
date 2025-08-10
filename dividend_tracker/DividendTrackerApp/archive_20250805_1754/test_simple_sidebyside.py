import tkinter as tk
from datetime import datetime

def create_test_popup():
    # Create main window
    root = tk.Tk()
    root.title("🎯 Dividend Processing Complete!")
    root.geometry("900x600")
    root.configure(bg="#1e1e2e")
    
    # Create main frame
    main_frame = tk.Frame(root, bg="#1e1e2e")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, 
                          text="🎯 WEEKLY DIVIDEND PROCESSING COMPLETE!", 
                          font=("Arial", 18, "bold"), 
                          bg="#1e1e2e", fg="#4ade80")
    title_label.pack(pady=20)
    
    # ACCOUNT BREAKDOWN SECTION WITH SIDE-BY-SIDE LAYOUT
    accounts_frame = tk.LabelFrame(main_frame, text="🏦 ACCOUNT BREAKDOWN", 
                                 font=("Arial", 14, "bold"), 
                                 bg="#2d3748", fg="#90cdf4", 
                                 relief="raised", bd=2)
    accounts_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create two-column container
    columns_container = tk.Frame(accounts_frame, bg="#2d3748")
    columns_container.pack(fill="both", expand=True, padx=10, pady=10)
    
    # LEFT COLUMN - DIVIDEND ACCOUNTS
    left_frame = tk.LabelFrame(columns_container, text="💰 DIVIDEND ACCOUNTS", 
                              font=("Arial", 12, "bold"), 
                              bg="#2d3748", fg="#90cdf4", 
                              relief="raised", bd=1)
    left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
    
    # Sample dividend account data
    accounts = [
        ("E*TRADE IRA", 210683.95, 18, 17.2, "#4ade80"),
        ("E*TRADE Taxable", 58545.98, 6, 15.8, "#60a5fa"),
        ("Schwab IRA", 15245.50, 3, 12.5, "#f59e0b"),
        ("Schwab Individual", 8120.75, 1, 18.9, "#ef4444")
    ]
    
    for name, value, positions, yield_pct, color in accounts:
        account_frame = tk.Frame(left_frame, bg="#374151", relief="raised", bd=1)
        account_frame.pack(fill="x", padx=5, pady=3)
        
        # Account header
        header_frame = tk.Frame(account_frame, bg=color, height=25)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"✅ {name}", font=("Arial", 10, "bold"), 
                bg=color, fg="white").pack(side="left", padx=8, pady=3)
        
        # Account details
        details_frame = tk.Frame(account_frame, bg="#374151")
        details_frame.pack(fill="x", padx=8, pady=4)
        
        tk.Label(details_frame, 
                text=f"${value:,.2f}  |  {positions} pos  |  {yield_pct}% yield", 
                font=("Arial", 9), bg="#374151", fg="white").pack(side="left")
    
    # RIGHT COLUMN - WEEKLY PORTFOLIO CHANGES
    right_frame = tk.LabelFrame(columns_container, text="📈 WEEKLY CHANGES", 
                               font=("Arial", 12, "bold"), 
                               bg="#2d3748", fg="#90cdf4", 
                               relief="raised", bd=1)
    right_frame.pack(side="right", fill="both", expand=True, padx=(10, 0))
    
    # Weekly changes data
    weekly_changes = [
        ("E*TRADE IRA", 208156.42, 210683.95, 2527.53, 1.21),
        ("E*TRADE Taxable", 57891.22, 58545.98, 654.76, 1.13), 
        ("Schwab IRA", 15089.15, 15245.50, 156.35, 1.04),
        ("Schwab Individual", 7995.80, 8120.75, 124.95, 1.56)
    ]
    
    # Create table header
    header_text = f"{'Account':<15} {'Last Week':<12} {'Current':<12} {'Change':<10}"
    tk.Label(right_frame, text=header_text, font=("Arial", 9, "bold"), 
            bg="#374151", fg="#90cdf4", justify="left").pack(fill="x", padx=5, pady=5)
    
    # Add data rows
    total_last_week = 0
    total_current_week = 0
    
    for account, last_week, current_week, change_dollars, change_percent in weekly_changes:
        total_last_week += last_week
        total_current_week += current_week
        
        # Determine change color
        change_color = "#4ade80" if change_dollars > 0 else "#ef4444"
        change_symbol = "+" if change_dollars > 0 else ""
        
        # Shortened account name
        short_name = account.replace("E*TRADE ", "ET ").replace("Schwab ", "SC ")
        
        # Create row
        row_frame = tk.Frame(right_frame, bg="#374151", relief="raised", bd=1)
        row_frame.pack(fill="x", padx=5, pady=1)
        
        row_text = f"{short_name:<15} ${last_week/1000:.0f}k{'':<7} ${current_week/1000:.0f}k{'':<7} {change_symbol}{change_percent:.1f}%"
        tk.Label(row_frame, text=row_text, font=("Arial", 8), 
                bg="#374151", fg="#ffffff", justify="left").pack(fill="x", padx=5, pady=2)
    
    # Total row
    total_change = total_current_week - total_last_week
    total_change_percent = (total_change / total_last_week * 100) if total_last_week > 0 else 0
    total_color = "#4ade80" if total_change > 0 else "#ef4444"
    total_symbol = "+" if total_change > 0 else ""
    
    total_frame = tk.Frame(right_frame, bg="#1f2937", relief="raised", bd=2)
    total_frame.pack(fill="x", padx=5, pady=(5, 5))
    
    total_text = f"{'TOTAL':<15} ${total_last_week/1000:.0f}k{'':<7} ${total_current_week/1000:.0f}k{'':<7} {total_symbol}{total_change_percent:.1f}%"
    tk.Label(total_frame, text=total_text, font=("Arial", 9, "bold"), 
            bg="#1f2937", fg="#fbbf24", justify="left").pack(fill="x", padx=5, pady=5)
    
    # Close button
    close_btn = tk.Button(main_frame, text="✅ Close", font=("Arial", 12, "bold"), 
                         bg="#4ade80", fg="white", width=12, height=1,
                         command=root.destroy)
    close_btn.pack(pady=20)
    
    # Show the window
    root.mainloop()

if __name__ == "__main__":
    print("🎯 Creating SIMPLE side-by-side test popup...")
    create_test_popup()
