#!/usr/bin/env python3
"""
Test GUI Popup - Beautiful Dividend Completion Display
This shows exactly what you'll see when dividend processing completes
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime

def create_test_popup():
    """Create and display the beautiful dividend completion popup TEST VERSION"""
    
    # Create main window
    root = tk.Tk()
    root.title("🎉 Dividend Tracker - Processing Complete! [TEST]")
    root.geometry("1200x700")  # Made wider for side-by-side layout
    root.configure(bg="#1e1e2e")
    
    # Make window stay on top and centered
    root.attributes('-topmost', True)
    root.update_idletasks()
    
    # Center the window
    x = (root.winfo_screenwidth() // 2) - (1200 // 2)  # Updated for new width
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"1200x700+{x}+{y}")

    # Main header
    header_frame = tk.Frame(root, bg="#4c956c", height=80)
    header_frame.pack(fill="x", padx=10, pady=(10, 0))
    header_frame.pack_propagate(False)
    
    header_label = tk.Label(header_frame, 
                           text="🎉 DIVIDEND TRACKER COMPLETE! 🎉", 
                           font=("Arial", 18, "bold"), 
                           bg="#4c956c", fg="white")
    header_label.pack(expand=True)
    
    # Scrollable content frame
    canvas = tk.Canvas(root, bg="#1e1e2e", highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#1e1e2e")
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Add mouse wheel scrolling support
    def on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def bind_mousewheel(event):
        canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def unbind_mousewheel(event):
        canvas.unbind_all("<MouseWheel>")
    
    # Bind mouse wheel events when mouse enters/leaves the canvas
    canvas.bind('<Enter>', bind_mousewheel)
    canvas.bind('<Leave>', unbind_mousewheel)
    
    # PORTFOLIO SUMMARY SECTION
    summary_frame = tk.LabelFrame(scrollable_frame, text="📊 PORTFOLIO SUMMARY", 
                                font=("Arial", 14, "bold"), 
                                bg="#2d3748", fg="#90cdf4", 
                                relief="raised", bd=2)
    summary_frame.pack(fill="x", padx=20, pady=15)
    
    # Your actual portfolio data (sample based on what we know)
    portfolio_data = {
        "total_value": 269229.93,
        "dividend_yield": 16.90,
        "dividend_positions": 24,
        "monthly_income": 1892.50,
        "annual_income": 22710.00
    }
    
    # Create metrics in a grid
    metrics = [
        ("💰 Total Portfolio Value", f"${portfolio_data['total_value']:,.2f}", "#4ade80"),
        ("📈 Average Dividend Yield", f"{portfolio_data['dividend_yield']:.2f}%", "#60a5fa"),
        ("🏢 Dividend Positions", f"{portfolio_data['dividend_positions']}", "#f59e0b"),
        ("💵 Monthly Income", f"${portfolio_data['monthly_income']:,.2f}", "#34d399"),
        ("💰 Annual Income", f"${portfolio_data['annual_income']:,.2f}", "#fbbf24")
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        row = i // 2
        col = i % 2
        
        metric_frame = tk.Frame(summary_frame, bg="#374151", relief="raised", bd=1)
        metric_frame.grid(row=row, column=col, padx=10, pady=8, sticky="ew")
        
        tk.Label(metric_frame, text=label, font=("Arial", 10), 
                bg="#374151", fg="white").pack(pady=(5, 0))
        tk.Label(metric_frame, text=value, font=("Arial", 14, "bold"), 
                bg="#374151", fg=color).pack(pady=(0, 5))
    
    # Configure grid weights
    for i in range(2):
        summary_frame.columnconfigure(i, weight=1)
    
    # DIVIDEND SUMMARY SECTION - FULL WIDTH AT TOP
    summary_frame = tk.LabelFrame(scrollable_frame, text="💰 DIVIDEND PORTFOLIO SUMMARY", 
                                 font=("Arial", 16, "bold"), 
                                 bg="#2d3748", fg="#90cdf4", 
                                 relief="raised", bd=2)
    summary_frame.pack(fill="x", padx=20, pady=15)
    
    # Key metrics in a grid layout
    metrics_container = tk.Frame(summary_frame, bg="#2d3748")
    metrics_container.pack(fill="x", padx=20, pady=15)
    
    metrics = [
        ("Total Holdings", "28 dividend-paying stocks", "#4ade80"),
        ("High-Yield Focus", "All holdings yield ≥ 4.0%", "#60a5fa"),
        ("Total Portfolio Value", "$292,596.18", "#f59e0b"),
        ("Weighted Average Yield", "16.8%", "#ef4444")
    ]
    
    for i, (label, value, color) in enumerate(metrics):
        metric_frame = tk.Frame(metrics_container, bg="#374151", relief="raised", bd=2)
        metric_frame.grid(row=i//2, column=i%2, padx=10, pady=8, sticky="ew")
        
        tk.Label(metric_frame, text=label, font=("Arial", 12, "bold"), 
                bg="#374151", fg="#d1d5db").pack(pady=(8, 4))
        tk.Label(metric_frame, text=value, font=("Arial", 14, "bold"), 
                bg="#374151", fg=color).pack(pady=(4, 8))
    
    # Configure grid weights for even spacing
    metrics_container.grid_columnconfigure(0, weight=1)
    metrics_container.grid_columnconfigure(1, weight=1)
    
    # Processing info
    processing_frame = tk.Frame(summary_frame, bg="#2d3748")
    processing_frame.pack(fill="x", padx=20, pady=(0, 15))
    
    processing_text = f"""⏰ Processing Time: 2.3 seconds | 🗓️ Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"""
    tk.Label(processing_frame, text=processing_text, font=("Arial", 12), 
            bg="#2d3748", fg="#a3a3a3").pack()

    # ACCOUNT BREAKDOWN SECTION - USING PANEDWINDOW FOR TWO COLUMNS
    accounts_outer_frame = tk.LabelFrame(scrollable_frame, text="🏦 DETAILED BREAKDOWN", 
                                        font=("Arial", 16, "bold"), 
                                        bg="#2d3748", fg="#90cdf4", 
                                        relief="raised", bd=2)
    accounts_outer_frame.pack(fill="x", padx=20, pady=15)
    
    # Use PanedWindow for guaranteed two-column layout with adjusted widths
    paned_window = tk.PanedWindow(accounts_outer_frame, orient=tk.HORIZONTAL, 
                                 sashwidth=8, bg="#2d3748", 
                                 sashrelief=tk.RAISED)
    paned_window.pack(fill="both", expand=True, padx=10, pady=10)
    
    # LEFT PANE - DIVIDEND ACCOUNT BREAKDOWN (slightly narrower)
    dividend_column = tk.LabelFrame(paned_window, text="💰 DIVIDEND ACCOUNTS", 
                                   font=("Arial", 14, "bold"), bg="#2d3748", fg="#90cdf4", 
                                   relief="raised", bd=2)
    paned_window.add(dividend_column, minsize=380, width=420)
    
    # Detailed account data
    accounts = [
        ("E*TRADE IRA", 210683.95, 18, 17.2, "#4ade80", "Primary retirement account"),
        ("E*TRADE Taxable", 58545.98, 6, 15.8, "#60a5fa", "Tax-efficient holdings"),
        ("Schwab IRA", 15245.50, 3, 12.5, "#f59e0b", "Secondary retirement"),
        ("Schwab Individual", 8120.75, 1, 18.9, "#ef4444", "High-yield focused")
    ]
    
    for name, value, positions, yield_pct, color, description in accounts:
        account_frame = tk.Frame(dividend_column, bg="#374151", relief="raised", bd=2)
        account_frame.pack(fill="x", padx=10, pady=6)
        
        # Account header with enhanced info
        header_frame = tk.Frame(account_frame, bg=color, height=35)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text=f"✅ {name}", font=("Arial", 12, "bold"), 
                bg=color, fg="white").pack(side="left", padx=12, pady=8)
        
        # Account details with larger fonts
        details_frame = tk.Frame(account_frame, bg="#374151")
        details_frame.pack(fill="x", padx=12, pady=8)
        
        # Value and yield on first line
        tk.Label(details_frame, 
                text=f"💰 ${value:,.2f} | 🎯 {yield_pct}% yield | 📈 {positions} positions", 
                font=("Arial", 12, "bold"), bg="#374151", fg="white").pack(anchor="w")
        
        # Description on second line
        tk.Label(details_frame, text=f"📝 {description}", 
                font=("Arial", 11), bg="#374151", fg="#d1d5db").pack(anchor="w", pady=(4, 0))
        
        # Average position size
        avg_position = value / positions if positions > 0 else 0
        tk.Label(details_frame, text=f"📊 Average position: ${avg_position:,.0f}", 
                font=("Arial", 11), bg="#374151", fg="#a3a3a3").pack(anchor="w", pady=(2, 0))
    
    # NARROW TOP DIVIDEND PERFORMERS SECTION (preferred)
    narrow_performers_frame = tk.LabelFrame(dividend_column, text="🏆 TOP PERFORMERS (COMPACT)", 
                                           font=("Arial", 13, "bold"), 
                                           bg="#2d3748", fg="#fbbf24", 
                                           relief="raised", bd=2)
    narrow_performers_frame.pack(fill="x", padx=10, pady=12)
    
    # Compact performer list with larger fonts
    compact_performers = [
        ("REML", "6.8%", "+3.2%", "#4ade80"),
        ("JEPI", "7.1%", "+2.8%", "#4ade80"), 
        ("PFF", "5.9%", "+2.1%", "#60a5fa"),
        ("VYM", "4.2%", "+1.5%", "#60a5fa")
    ]
    
    for ticker, yield_pct, performance, color in compact_performers:
        perf_row = tk.Frame(narrow_performers_frame, bg="#374151", relief="ridge", bd=1)
        perf_row.pack(fill="x", padx=8, pady=4)
        
        # Ticker
        tk.Label(perf_row, text=ticker, font=("Arial", 12, "bold"), 
                bg="#374151", fg="#ffffff").pack(side="left", padx=8, pady=6)
        
        # Yield
        tk.Label(perf_row, text=f"{yield_pct} yield", font=("Arial", 11), 
                bg="#374151", fg="#4ade80").pack(side="left", padx=6)
        
        # Performance  
        tk.Label(perf_row, text=performance, font=("Arial", 11, "bold"), 
                bg="#374151", fg=color).pack(side="right", padx=8)
    
    # RIGHT PANE - WEEKLY PORTFOLIO PERFORMANCE (wider for larger fonts)
    portfolio_column = tk.LabelFrame(paned_window, text="📈 WEEKLY PORTFOLIO PERFORMANCE", 
                                    font=("Arial", 14, "bold"), bg="#374151", fg="#90cdf4", 
                                    relief="raised", bd=2)
    paned_window.add(portfolio_column, minsize=480, width=520)
    
    # Portfolio summary header
    summary_label = tk.Label(portfolio_column, text="📊 WEEK-OVER-WEEK ANALYSIS", 
                            font=("Arial", 13, "bold"), bg="#374151", fg="#90cdf4")
    summary_label.pack(pady=12)
    
    # Detailed weekly data with all metrics
    weekly_data = [
        ("E*TRADE IRA", 208156.42, 210683.95, 2527.53, 1.21, "#4ade80"),
        ("E*TRADE Taxable", 57891.22, 58545.98, 654.76, 1.13, "#60a5fa"), 
        ("Schwab IRA", 15089.15, 15245.50, 156.35, 1.04, "#f59e0b"),
        ("Schwab Individual", 7995.80, 8120.75, 124.95, 1.56, "#ef4444")
    ]
    
    # Create comprehensive table header
    header_frame = tk.Frame(portfolio_column, bg="#1f2937", relief="raised", bd=2)
    header_frame.pack(fill="x", padx=10, pady=(0, 8))
    
    header_labels = ["Account", "Last Week", "Current Week", "Change ($)", "Change (%)"]
    header_widths = [150, 110, 110, 110, 90]
    
    for i, (label, width) in enumerate(zip(header_labels, header_widths)):
        header_frame.grid_columnconfigure(i, minsize=width)
        tk.Label(header_frame, text=label, font=("Arial", 11, "bold"), 
                bg="#1f2937", fg="#90cdf4").grid(row=0, column=i, padx=4, pady=8, sticky="ew")
    
    # Account performance rows with detailed data
    total_last_week = 0
    total_current_week = 0
    
    for account, last_week, current_week, change_dollars, change_percent, color in weekly_data:
        total_last_week += last_week
        total_current_week += current_week
        
        # Determine change colors and symbols
        change_color = "#4ade80" if change_dollars > 0 else "#ef4444" if change_dollars < 0 else "#6b7280"
        change_symbol = "+" if change_dollars > 0 else ""
        
        # Create detailed row
        row_frame = tk.Frame(portfolio_column, bg="#4a5568", relief="raised", bd=1)
        row_frame.pack(fill="x", padx=10, pady=3)
        
        # Configure grid for this row
        for i, width in enumerate(header_widths):
            row_frame.grid_columnconfigure(i, minsize=width)
        
        # Account name with color coding
        tk.Label(row_frame, text=account, font=("Arial", 11, "bold"), 
                bg="#4a5568", fg=color).grid(row=0, column=0, padx=4, pady=6, sticky="w")
        
        # Last week value
        tk.Label(row_frame, text=f"${last_week:,.2f}", font=("Arial", 11), 
                bg="#4a5568", fg="#d1d5db").grid(row=0, column=1, padx=4, pady=6)
        
        # Current week value  
        tk.Label(row_frame, text=f"${current_week:,.2f}", font=("Arial", 11, "bold"), 
                bg="#4a5568", fg="#ffffff").grid(row=0, column=2, padx=4, pady=6)
        
        # Dollar change
        tk.Label(row_frame, text=f"{change_symbol}${change_dollars:,.2f}", font=("Arial", 11, "bold"), 
                bg="#4a5568", fg=change_color).grid(row=0, column=3, padx=4, pady=6)
        
        # Percentage change
        tk.Label(row_frame, text=f"{change_symbol}{change_percent:.2f}%", font=("Arial", 11, "bold"), 
                bg="#4a5568", fg=change_color).grid(row=0, column=4, padx=4, pady=6)
    
    # Calculate total portfolio changes
    total_change_dollars = total_current_week - total_last_week
    total_change_percent = (total_change_dollars / total_last_week * 100) if total_last_week > 0 else 0
    total_change_color = "#4ade80" if total_change_dollars > 0 else "#ef4444" if total_change_dollars < 0 else "#6b7280"
    total_change_symbol = "+" if total_change_dollars > 0 else ""
    
    # Total portfolio summary row
    total_frame = tk.Frame(portfolio_column, bg="#1f2937", relief="raised", bd=3)
    total_frame.pack(fill="x", padx=10, pady=(12, 8))
    
    # Configure grid for totals
    for i, width in enumerate(header_widths):
        total_frame.grid_columnconfigure(i, minsize=width)
    
    tk.Label(total_frame, text="TOTAL PORTFOLIO", font=("Arial", 12, "bold"), 
            bg="#1f2937", fg="#fbbf24").grid(row=0, column=0, padx=4, pady=10, sticky="w")
    
    tk.Label(total_frame, text=f"${total_last_week:,.2f}", font=("Arial", 12, "bold"), 
            bg="#1f2937", fg="#d1d5db").grid(row=0, column=1, padx=4, pady=10)
    
    tk.Label(total_frame, text=f"${total_current_week:,.2f}", font=("Arial", 12, "bold"), 
            bg="#1f2937", fg="#fbbf24").grid(row=0, column=2, padx=4, pady=10)
    
    tk.Label(total_frame, text=f"{total_change_symbol}${total_change_dollars:,.2f}", font=("Arial", 12, "bold"), 
            bg="#1f2937", fg=total_change_color).grid(row=0, column=3, padx=4, pady=10)
    
    tk.Label(total_frame, text=f"{total_change_symbol}{total_change_percent:.2f}%", font=("Arial", 12, "bold"), 
            bg="#1f2937", fg=total_change_color).grid(row=0, column=4, padx=4, pady=10)
    
    # Additional portfolio insights
    insights_frame = tk.Frame(portfolio_column, bg="#374151")
    insights_frame.pack(fill="x", padx=10, pady=(12, 8))
    
    tk.Label(insights_frame, text="📈 PORTFOLIO INSIGHTS", font=("Arial", 12, "bold"), 
            bg="#374151", fg="#90cdf4").pack(pady=(8, 10))
    
    # Calculate some insights
    best_performer = max(weekly_data, key=lambda x: x[4])
    worst_performer = min(weekly_data, key=lambda x: x[4])
    
    insights_text = f"""🏆 Best Performer: {best_performer[0]} (+{best_performer[4]:.2f}%)
📉 Needs Attention: {worst_performer[0]} (+{worst_performer[4]:.2f}%)
💰 Net Weekly Gain: {total_change_symbol}${abs(total_change_dollars):,.2f}
📊 Portfolio Trend: {"Positive Growth" if total_change_dollars > 0 else "Correction Phase"}"""
    
    tk.Label(insights_frame, text=insights_text, font=("Arial", 11), 
            bg="#374151", fg="#4ade80", justify="left").pack(padx=12, pady=(0, 12))
    
    # TOP PERFORMERS SECTION
    performers_frame = tk.LabelFrame(scrollable_frame, text="🏆 TOP DIVIDEND PERFORMERS", 
                                   font=("Arial", 14, "bold"), 
                                   bg="#2d3748", fg="#90cdf4", 
                                   relief="raised", bd=2)
    performers_frame.pack(fill="x", padx=20, pady=15)
    
    # Your top performers from what we've seen
    performers = [
        ("🥇", "BITO", 53.4, 4158.00),
        ("🥈", "RYLD", 13.1, 11636.70),
        ("🥉", "OFS", 16.4, 2862.65),
        ("4️⃣", "ACP", 15.6, 5548.76),
        ("5️⃣", "AGNC", 15.2, 3139.38)
    ]
    
    for medal, ticker, yield_pct, value in performers:
        perf_frame = tk.Frame(performers_frame, bg="#374151", relief="raised", bd=1)
        perf_frame.pack(fill="x", padx=10, pady=3)
        
        content_frame = tk.Frame(perf_frame, bg="#374151")
        content_frame.pack(fill="x", padx=15, pady=8)
        
        # Medal and ticker
        tk.Label(content_frame, text=f"{medal} {ticker}", font=("Arial", 12, "bold"), 
                bg="#374151", fg="#fbbf24").pack(side="left")
        
        # Yield and value
        tk.Label(content_frame, text=f"{yield_pct}% yield", font=("Arial", 11), 
                bg="#374151", fg="#4ade80").pack(side="right")
        tk.Label(content_frame, text=f"${value:,.2f}", font=("Arial", 11), 
                bg="#374151", fg="#60a5fa").pack(side="right", padx=(0, 20))
    
    # STATISTICS SECTION
    stats_frame = tk.LabelFrame(scrollable_frame, text="� COMPLETION STATISTICS", 
                               font=("Arial", 14, "bold"), 
                               bg="#2d3748", fg="#90cdf4", 
                               relief="raised", bd=2)
    stats_frame.pack(fill="x", padx=20, pady=15)
    
    stats_text = f"""✅ Total Holdings: 28 dividend-paying stocks
🎯 High-Yield Focus: All holdings yield ≥ 4.0%
💰 Total Portfolio Value: $292,596.18
📈 Weighted Average Yield: 16.8%
⏰ Processing Time: 2.3 seconds
🗓️ Last Updated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"""
    
    tk.Label(stats_frame, text=stats_text, font=("Arial", 11), 
            bg="#2d3748", fg="#f59e0b", justify="left").pack(padx=20, pady=15)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
    scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
    
    # BOTTOM BUTTONS SECTION
    button_frame = tk.Frame(root, bg="#1e1e2e", height=80)
    button_frame.pack(fill="x", padx=10, pady=(0, 10))
    button_frame.pack_propagate(False)
    
    # Success message
    success_label = tk.Label(button_frame, 
                           text="✅ SUCCESS! Your dividend portfolio has been updated and analyzed.", 
                           font=("Arial", 11, "bold"), 
                           bg="#1e1e2e", fg="#4ade80")
    success_label.pack(pady=(5, 0))
    
    # Next steps message
    next_label = tk.Label(button_frame, 
                         text="📋 Next: Weekly 401k amount update (only manual step needed)", 
                         font=("Arial", 10), 
                         bg="#1e1e2e", fg="#90cdf4")
    next_label.pack()
    
    # Time stamp
    time_label = tk.Label(button_frame, 
                         text=f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         font=("Arial", 9), 
                         bg="#1e1e2e", fg="#6b7280")
    time_label.pack()
    
    # Buttons
    buttons_container = tk.Frame(button_frame, bg="#1e1e2e")
    buttons_container.pack(pady=5)
    
    close_btn = tk.Button(buttons_container, text="✅ Close", font=("Arial", 12, "bold"), 
                         bg="#4ade80", fg="white", width=12, height=1,
                         command=root.destroy)
    close_btn.pack(side="left", padx=10)
    
    def open_excel():
        print("📊 Opening Excel report...")
        root.destroy()
    
    excel_btn = tk.Button(buttons_container, text="📊 Open Excel Report", font=("Arial", 12, "bold"), 
                         bg="#60a5fa", fg="white", width=15, height=1,
                         command=open_excel)
    excel_btn.pack(side="left", padx=10)
    
    # Remove topmost after 3 seconds so it doesn't stay on top forever
    def remove_topmost():
        root.attributes('-topmost', False)
    
    root.after(3000, remove_topmost)
    
    print("🎉 TEST POPUP LAUNCHED!")
    print("   This beautiful popup will appear automatically when your weekend dividend processing completes.")
    print("   Click 'Close' or 'Open Excel Report' when done reviewing.")
    print("")
    
    # Show the window
    root.mainloop()

if __name__ == "__main__":
    print("🎯 Creating test dividend completion popup...")
    create_test_popup()
