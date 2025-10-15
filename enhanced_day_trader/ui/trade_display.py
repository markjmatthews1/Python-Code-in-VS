#!/usr/bin/env python3
"""
Trade Display System for Enhanced Day Trader
==========================================

Beautiful, colorful trade tracking display with Arial 12+ font.
Real-time updates with comprehensive trade metrics.

Features:
- Colorful trade status indicators
- Arial 12+ font for readability  
- Real-time P&L tracking
- Daily and total performance
- Active positions monitoring
- Trade history with details

Author: GitHub Copilot
Date: October 15, 2025
"""

import tkinter as tk
from tkinter import ttk, font
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Callable
import threading
import time
import webbrowser

from core.paper_trader import paper_trader, Trade

class TradeDisplayWindow:
    """
    Beautiful trade tracking display with colorful interface
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced Day Trader - Trade Tracking")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1e1e1e')  # Dark background
        
        # Web dashboard callback
        self.web_dashboard_callback = None
        
        # Define colors
        self.colors = {
            'bg_dark': '#1e1e1e',
            'bg_medium': '#2d2d2d', 
            'bg_light': '#3e3e3e',
            'text_white': '#ffffff',
            'text_gray': '#cccccc',
            'profit_green': '#00ff88',
            'loss_red': '#ff4444',
            'neutral_blue': '#4488ff',
            'warning_orange': '#ffaa00',
            'accent_purple': '#aa44ff'
        }
        
        # Define fonts (Arial 12+)
        self.fonts = {
            'title': font.Font(family='Arial', size=16, weight='bold'),
            'header': font.Font(family='Arial', size=14, weight='bold'),
            'body': font.Font(family='Arial', size=12),
            'large': font.Font(family='Arial', size=14),
            'small': font.Font(family='Arial', size=10)
        }
        
        # Create main layout
        self.create_layout()
        
        # Start update thread
        self.running = True
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_layout(self):
        """Create the main layout with all components"""
        
        # Main title
        title_frame = tk.Frame(self.root, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', padx=10, pady=5)
        
        title_label = tk.Label(
            title_frame,
            text="🚀 Enhanced Day Trader - Live Trade Tracking",
            font=self.fonts['title'],
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_dark']
        )
        title_label.pack(side='left')
        
        # Add web dashboard button
        web_button = tk.Button(
            title_frame,
            text="🌐 Open Web Dashboard",
            font=self.fonts['body'],
            fg=self.colors['text_white'],
            bg=self.colors['neutral_blue'],
            activebackground=self.colors['accent_purple'],
            activeforeground=self.colors['text_white'],
            relief='raised',
            bd=2,
            padx=15,
            pady=5,
            command=self.open_web_dashboard
        )
        web_button.pack(side='right', padx=10)
        
        # Create main container with scrollable frame
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Performance summary section
        self.create_performance_section(main_container)
        
        # Active trades section
        self.create_active_trades_section(main_container)
        
        # Recent trades section
        self.create_recent_trades_section(main_container)
        
        # Update initial data
        self.update_display()
    
    def create_performance_section(self, parent):
        """Create performance summary section"""
        perf_frame = tk.LabelFrame(
            parent,
            text="📊 Performance Summary",
            font=self.fonts['header'],
            fg=self.colors['text_white'],
            bg=self.colors['bg_medium'],
            bd=2,
            relief='groove'
        )
        perf_frame.pack(fill='x', pady=5)
        
        # Create grid for performance metrics
        metrics_frame = tk.Frame(perf_frame, bg=self.colors['bg_medium'])
        metrics_frame.pack(fill='x', padx=10, pady=5)
        
        # Performance labels (will be updated dynamically)
        self.perf_labels = {}
        
        # Row 1: Balance and P&L
        row1_frame = tk.Frame(metrics_frame, bg=self.colors['bg_medium'])
        row1_frame.pack(fill='x', pady=2)
        
        self.perf_labels['balance'] = tk.Label(
            row1_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['balance'].pack(side='left', padx=20)
        
        self.perf_labels['total_pnl'] = tk.Label(
            row1_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['total_pnl'].pack(side='left', padx=20)
        
        self.perf_labels['today_pnl'] = tk.Label(
            row1_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['today_pnl'].pack(side='left', padx=20)
        
        # Row 2: Win rate and trades
        row2_frame = tk.Frame(metrics_frame, bg=self.colors['bg_medium'])
        row2_frame.pack(fill='x', pady=2)
        
        self.perf_labels['win_rate'] = tk.Label(
            row2_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['win_rate'].pack(side='left', padx=20)
        
        self.perf_labels['total_trades'] = tk.Label(
            row2_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['total_trades'].pack(side='left', padx=20)
        
        self.perf_labels['active_positions'] = tk.Label(
            row2_frame, font=self.fonts['large'], bg=self.colors['bg_medium']
        )
        self.perf_labels['active_positions'].pack(side='left', padx=20)
    
    def create_active_trades_section(self, parent):
        """Create active trades section"""
        active_frame = tk.LabelFrame(
            parent,
            text="🟢 Active Positions",
            font=self.fonts['header'],
            fg=self.colors['profit_green'],
            bg=self.colors['bg_medium'],
            bd=2,
            relief='groove'
        )
        active_frame.pack(fill='x', pady=5)
        
        # Create treeview for active trades
        columns = ('Ticker', 'Direction', 'Qty', 'Entry Price', 'Current Price', 'Unrealized P&L', 'Open Time')
        
        self.active_tree = ttk.Treeview(active_frame, columns=columns, show='headings', height=6)
        
        # Configure columns
        for col in columns:
            self.active_tree.heading(col, text=col)
            self.active_tree.column(col, width=120, anchor='center')
        
        # Configure treeview style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background=self.colors['bg_light'], 
                       foreground=self.colors['text_white'], font=self.fonts['body'])
        style.configure('Treeview.Heading', background=self.colors['bg_dark'],
                       foreground=self.colors['text_white'], font=self.fonts['header'])
        
        # Add scrollbar
        active_scroll = ttk.Scrollbar(active_frame, orient='vertical', command=self.active_tree.yview)
        self.active_tree.configure(yscrollcommand=active_scroll.set)
        
        self.active_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        active_scroll.pack(side='right', fill='y')
    
    def create_recent_trades_section(self, parent):
        """Create recent trades section"""
        recent_frame = tk.LabelFrame(
            parent,
            text="📈 Recent Closed Trades",
            font=self.fonts['header'],
            fg=self.colors['neutral_blue'],
            bg=self.colors['bg_medium'],
            bd=2,
            relief='groove'
        )
        recent_frame.pack(fill='both', expand=True, pady=5)
        
        # Create treeview for recent trades
        columns = ('Trade ID', 'Ticker', 'Direction', 'Qty', 'Entry', 'Exit', 'P&L', 'P&L%', 'Duration', 'Status')
        
        self.recent_tree = ttk.Treeview(recent_frame, columns=columns, show='headings', height=10)
        
        # Configure columns
        column_widths = {'Trade ID': 100, 'Ticker': 60, 'Direction': 80, 'Qty': 60, 
                        'Entry': 80, 'Exit': 80, 'P&L': 100, 'P&L%': 80, 'Duration': 100, 'Status': 120}
        
        for col in columns:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=column_widths.get(col, 100), anchor='center')
        
        # Add scrollbar
        recent_scroll = ttk.Scrollbar(recent_frame, orient='vertical', command=self.recent_tree.yview)
        self.recent_tree.configure(yscrollcommand=recent_scroll.set)
        
        self.recent_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        recent_scroll.pack(side='right', fill='y')
    
    def update_performance_display(self, summary: Dict):
        """Update performance metrics display"""
        
        # Balance
        balance_color = self.colors['profit_green'] if summary['total_pnl'] >= 0 else self.colors['loss_red']
        self.perf_labels['balance'].config(
            text=f"💰 Balance: ${summary['current_balance']:,.2f}",
            fg=balance_color
        )
        
        # Total P&L
        pnl_color = self.colors['profit_green'] if summary['total_pnl'] >= 0 else self.colors['loss_red']
        pnl_sign = "+" if summary['total_pnl'] >= 0 else ""
        self.perf_labels['total_pnl'].config(
            text=f"📊 Total P&L: {pnl_sign}${summary['total_pnl']:,.2f} ({summary['total_return_percent']:+.1f}%)",
            fg=pnl_color
        )
        
        # Today's P&L
        today_color = self.colors['profit_green'] if summary['today_pnl'] >= 0 else self.colors['loss_red']
        today_sign = "+" if summary['today_pnl'] >= 0 else ""
        self.perf_labels['today_pnl'].config(
            text=f"📅 Today: {today_sign}${summary['today_pnl']:,.2f}",
            fg=today_color
        )
        
        # Win rate
        win_rate_color = self.colors['profit_green'] if summary['win_rate'] >= 50 else self.colors['warning_orange']
        self.perf_labels['win_rate'].config(
            text=f"🎯 Win Rate: {summary['win_rate']:.1f}%",
            fg=win_rate_color
        )
        
        # Total trades
        self.perf_labels['total_trades'].config(
            text=f"📋 Total Trades: {summary['total_trades']} ({summary['winning_trades']}W/{summary['losing_trades']}L)",
            fg=self.colors['text_white']
        )
        
        # Active positions
        active_color = self.colors['neutral_blue'] if summary['active_positions'] > 0 else self.colors['text_gray']
        self.perf_labels['active_positions'].config(
            text=f"🟢 Active: {summary['active_positions']} positions",
            fg=active_color
        )
    
    def update_active_trades_display(self):
        """Update active trades display"""
        # Clear existing items
        for item in self.active_tree.get_children():
            self.active_tree.delete(item)
        
        # Add active trades
        for trade in paper_trader.active_trades.values():
            # Get current price (simulate for demo)
            current_price = trade.open_price * (1 + (0.01 * (hash(trade.trade_id) % 21 - 10) / 10))
            
            # Calculate unrealized P&L
            if trade.direction == 'LONG':
                unrealized_pnl = (current_price - trade.open_price) * trade.quantity
            else:
                unrealized_pnl = (trade.open_price - current_price) * trade.quantity
            
            # Format values
            values = (
                trade.ticker,
                trade.direction,
                f"{trade.quantity:,}",
                f"${trade.open_price:.2f}",
                f"${current_price:.2f}",
                f"${unrealized_pnl:+.2f}",
                trade.open_time.strftime("%m/%d %H:%M")
            )
            
            # Add to tree with color coding
            item = self.active_tree.insert('', 'end', values=values)
            
            # Color code based on P&L
            if unrealized_pnl > 0:
                self.active_tree.set(item, 'Unrealized P&L', f"+${unrealized_pnl:.2f}")
            elif unrealized_pnl < 0:
                self.active_tree.set(item, 'Unrealized P&L', f"-${abs(unrealized_pnl):.2f}")
    
    def update_recent_trades_display(self):
        """Update recent trades display"""
        # Clear existing items
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)
        
        # Get all trades (closed + active) sorted by time
        all_trades = []
        
        # Add closed trades
        all_trades.extend(paper_trader.closed_trades)
        
        # Add active trades
        for trade in paper_trader.active_trades.values():
            all_trades.append(trade)
        
        # Sort by open time (most recent first)
        all_trades.sort(key=lambda t: t.open_time, reverse=True)
        
        # Display the most recent 20 trades
        for trade in all_trades[:20]:
            if trade.close_time:
                duration = trade.close_time - trade.open_time
                duration_str = f"{duration.total_seconds()/3600:.1f}h"
            else:
                duration_str = "Active"
            
            # Format P&L with color indicators
            pnl_text = f"${trade.pnl:+.2f}" if trade.pnl != 0 else "$0.00"
            pnl_percent_text = f"{trade.pnl_percent:+.1f}%" if trade.pnl_percent != 0 else "0.0%"
            
            # Status with emoji
            status_map = {
                'CLOSED_TAKE_PROFIT': '🎯 Target Hit',
                'CLOSED_STOP_LOSS': '🛑 Stop Loss',
                'CLOSED_MANUAL': '✋ Manual Close',
                'CLOSED_TIME': '⏰ Time Exit',
                'OPEN': '🟢 Active'
            }
            status_display = status_map.get(trade.status, trade.status)
            
            values = (
                trade.trade_id,
                trade.ticker,
                trade.direction,
                f"{trade.quantity:,}",
                f"${trade.open_price:.2f}",
                f"${trade.close_price:.2f}" if trade.close_price else "Active",
                pnl_text,
                pnl_percent_text,
                duration_str,
                status_display
            )
            
            item = self.recent_tree.insert('', 'end', values=values)
    
    def add_web_button(self, callback: Callable):
        """Add web dashboard callback function"""
        self.web_dashboard_callback = callback
    
    def open_web_dashboard(self):
        """Open web dashboard in browser"""
        if self.web_dashboard_callback:
            self.web_dashboard_callback()
        else:
            # Fallback - try to open directly
            try:
                webbrowser.open("http://localhost:8051")
            except Exception as e:
                print(f"Error opening web dashboard: {e}")
    
    def update_display(self):
        """Update all display components"""
        try:
            # Get performance summary
            summary = paper_trader.get_performance_summary()
            
            # Update all sections
            self.update_performance_display(summary)
            self.update_active_trades_display()
            self.update_recent_trades_display()
            
        except Exception as e:
            print(f"Error updating display: {e}")
    
    def update_loop(self):
        """Background update loop"""
        while self.running:
            try:
                self.root.after(0, self.update_display)
                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Error in update loop: {e}")
                time.sleep(10)
    
    def on_closing(self):
        """Handle window closing"""
        self.running = False
        self.root.destroy()
    
    def show(self):
        """Show the display window"""
        self.root.mainloop()

def create_trade_display():
    """Create and return the trade display window"""
    display = TradeDisplayWindow()
    return display

if __name__ == "__main__":
    # Test the trade display
    print("🎨 Testing Trade Display System...")
    
    # Add some test trades
    test_signals = [
        {
            'symbol': 'XLK',
            'direction': 'BUY',
            'entry_price': 285.50,
            'stop_loss': 284.36,
            'take_profit': 287.78,
            'signal_strength': 0.65
        },
        {
            'symbol': 'XLF',
            'direction': 'SELL',
            'entry_price': 53.25,
            'stop_loss': 53.46,
            'take_profit': 52.82,
            'signal_strength': 0.58
        }
    ]
    
    for signal in test_signals:
        paper_trader.open_trade(signal)
    
    # Show display
    display = create_trade_display()
    display.show()