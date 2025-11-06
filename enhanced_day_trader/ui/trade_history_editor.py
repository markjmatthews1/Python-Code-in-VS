#!/usr/bin/env python3
"""
Trade History Editor for Enhanced Day Trader
============================================

View and manage closed trades with ability to delete incorrect entries.
Features:
- Colorful display with Arial 12+ fonts
- Filter by date, ticker, P&L
- Delete individual or multiple trades
- Export to CSV
- Statistics summary

Author: GitHub Copilot
Date: October 17, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
from typing import List

from core.paper_trader import paper_trader, Trade

class TradeHistoryEditor:
    """
    Trade history viewer and editor with delete functionality
    """
    
    def __init__(self):
        self.window = tk.Toplevel()
        self.window.title("Enhanced Day Trader - Trade History Editor")
        self.window.geometry("1600x900")
        self.window.configure(bg='#1e1e1e')
        
        # Colors
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
            'accent_purple': '#aa44ff',
            'delete_red': '#cc0000'
        }
        
        # Fonts (Arial 12+)
        self.fonts = {
            'title': ('Arial', 16, 'bold'),
            'header': ('Arial', 14, 'bold'),
            'body': ('Arial', 12),
            'large': ('Arial', 14),
            'small': ('Arial', 11)
        }
        
        # Selected trades for deletion
        self.selected_trades = set()
        
        # Create UI
        self.create_layout()
        self.load_trades()
        
    def create_layout(self):
        """Create the main layout"""
        
        # Title bar
        title_frame = tk.Frame(self.window, bg=self.colors['bg_dark'])
        title_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(
            title_frame,
            text="📊 Trade History Editor",
            font=self.fonts['title'],
            fg=self.colors['accent_purple'],
            bg=self.colors['bg_dark']
        ).pack(side='left')
        
        # Close button
        tk.Button(
            title_frame,
            text="✕ Close",
            font=self.fonts['body'],
            bg=self.colors['bg_medium'],
            fg=self.colors['text_white'],
            command=self.window.destroy
        ).pack(side='right', padx=5)
        
        # Statistics summary
        stats_frame = tk.Frame(self.window, bg=self.colors['bg_medium'])
        stats_frame.pack(fill='x', padx=10, pady=5)
        
        self.stats_labels = {}
        
        tk.Label(
            stats_frame,
            text="Summary:",
            font=self.fonts['header'],
            fg=self.colors['text_white'],
            bg=self.colors['bg_medium']
        ).pack(side='left', padx=10)
        
        self.stats_labels['total'] = tk.Label(
            stats_frame,
            text="Total: 0",
            font=self.fonts['body'],
            fg=self.colors['neutral_blue'],
            bg=self.colors['bg_medium']
        )
        self.stats_labels['total'].pack(side='left', padx=10)
        
        self.stats_labels['wins'] = tk.Label(
            stats_frame,
            text="Wins: 0",
            font=self.fonts['body'],
            fg=self.colors['profit_green'],
            bg=self.colors['bg_medium']
        )
        self.stats_labels['wins'].pack(side='left', padx=10)
        
        self.stats_labels['losses'] = tk.Label(
            stats_frame,
            text="Losses: 0",
            font=self.fonts['body'],
            fg=self.colors['loss_red'],
            bg=self.colors['bg_medium']
        )
        self.stats_labels['losses'].pack(side='left', padx=10)
        
        self.stats_labels['total_pnl'] = tk.Label(
            stats_frame,
            text="Total P&L: $0.00",
            font=self.fonts['body'],
            fg=self.colors['text_white'],
            bg=self.colors['bg_medium']
        )
        self.stats_labels['total_pnl'].pack(side='left', padx=10)
        
        # Filter controls
        filter_frame = tk.Frame(self.window, bg=self.colors['bg_medium'])
        filter_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            filter_frame,
            text="Filter:",
            font=self.fonts['body'],
            fg=self.colors['text_white'],
            bg=self.colors['bg_medium']
        ).pack(side='left', padx=5)
        
        tk.Label(
            filter_frame,
            text="Ticker:",
            font=self.fonts['body'],
            fg=self.colors['text_gray'],
            bg=self.colors['bg_medium']
        ).pack(side='left', padx=5)
        
        self.ticker_filter = tk.Entry(
            filter_frame,
            font=self.fonts['body'],
            bg=self.colors['bg_light'],
            fg=self.colors['text_white'],
            width=10
        )
        self.ticker_filter.pack(side='left', padx=5)
        
        tk.Button(
            filter_frame,
            text="🔍 Apply Filter",
            font=self.fonts['body'],
            bg=self.colors['neutral_blue'],
            fg=self.colors['text_white'],
            command=self.apply_filter
        ).pack(side='left', padx=5)
        
        tk.Button(
            filter_frame,
            text="🔄 Clear Filter",
            font=self.fonts['body'],
            bg=self.colors['bg_light'],
            fg=self.colors['text_white'],
            command=self.clear_filter
        ).pack(side='left', padx=5)
        
        # Action buttons
        action_frame = tk.Frame(self.window, bg=self.colors['bg_medium'])
        action_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Button(
            action_frame,
            text="🗑️ Delete Selected",
            font=self.fonts['body'],
            bg=self.colors['delete_red'],
            fg=self.colors['text_white'],
            command=self.delete_selected
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="✅ Select All",
            font=self.fonts['body'],
            bg=self.colors['bg_light'],
            fg=self.colors['text_white'],
            command=self.select_all
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="⬜ Deselect All",
            font=self.fonts['body'],
            bg=self.colors['bg_light'],
            fg=self.colors['text_white'],
            command=self.deselect_all
        ).pack(side='left', padx=5)
        
        tk.Button(
            action_frame,
            text="💾 Export to CSV",
            font=self.fonts['body'],
            bg=self.colors['neutral_blue'],
            fg=self.colors['text_white'],
            command=self.export_csv
        ).pack(side='left', padx=5)
        
        tk.Label(
            action_frame,
            text="",
            bg=self.colors['bg_medium']
        ).pack(side='left', expand=True)
        
        self.selection_label = tk.Label(
            action_frame,
            text="Selected: 0",
            font=self.fonts['body'],
            fg=self.colors['warning_orange'],
            bg=self.colors['bg_medium']
        )
        self.selection_label.pack(side='right', padx=10)
        
        # Trade list with scrollbar
        list_frame = tk.Frame(self.window, bg=self.colors['bg_dark'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Scrollbars
        vsb = ttk.Scrollbar(list_frame, orient='vertical')
        vsb.pack(side='right', fill='y')
        
        hsb = ttk.Scrollbar(list_frame, orient='horizontal')
        hsb.pack(side='bottom', fill='x')
        
        # Treeview for trades
        columns = ('Select', 'Trade ID', 'Ticker', 'Direction', 'Qty', 'Entry', 'Exit', 'P&L', 'P&L %', 'Duration', 'Open Time', 'Close Time', 'Status')
        
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=25
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.column('Select', width=60, anchor='center')
        self.tree.column('Trade ID', width=120, anchor='w')
        self.tree.column('Ticker', width=80, anchor='center')
        self.tree.column('Direction', width=80, anchor='center')
        self.tree.column('Qty', width=60, anchor='center')
        self.tree.column('Entry', width=90, anchor='e')
        self.tree.column('Exit', width=90, anchor='e')
        self.tree.column('P&L', width=100, anchor='e')
        self.tree.column('P&L %', width=80, anchor='e')
        self.tree.column('Duration', width=100, anchor='center')
        self.tree.column('Open Time', width=150, anchor='center')
        self.tree.column('Close Time', width=150, anchor='center')
        self.tree.column('Status', width=120, anchor='center')
        
        # Headers
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
        
        # Bind click event
        self.tree.bind('<Button-1>', self.on_click)
        
        self.tree.pack(fill='both', expand=True)
        
        # Configure tag colors
        self.tree.tag_configure('profit', background='#003300', foreground='#00ff88')
        self.tree.tag_configure('loss', background='#330000', foreground='#ff4444')
        self.tree.tag_configure('breakeven', background='#1e1e1e', foreground='#888888')
        self.tree.tag_configure('selected', background='#444444')
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'Treeview',
            background='#2d2d2d',
            foreground='white',
            fieldbackground='#2d2d2d',
            font=('Arial', 12)
        )
        style.configure('Treeview.Heading', font=('Arial', 12, 'bold'), background='#3e3e3e', foreground='white')
        style.map('Treeview', background=[('selected', '#444444')])
        
    def load_trades(self):
        """Load all closed trades"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.selected_trades.clear()
        
        # Load closed trades
        total_pnl = 0
        wins = 0
        losses = 0
        
        for trade in paper_trader.closed_trades:
            # Calculate duration
            if trade.close_time and trade.open_time:
                duration = trade.close_time - trade.open_time
                duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
            else:
                duration_str = "N/A"
            
            # Format values
            values = (
                '☐',  # Unchecked checkbox
                trade.trade_id,
                trade.ticker,
                trade.direction,
                f"{trade.quantity:,}",
                f"${trade.open_price:.2f}",
                f"${trade.close_price:.2f}" if trade.close_price else "N/A",
                f"${trade.pnl:+.2f}",
                f"{trade.pnl_percent:+.2f}%",
                duration_str,
                trade.open_time.strftime("%Y-%m-%d %H:%M:%S"),
                trade.close_time.strftime("%Y-%m-%d %H:%M:%S") if trade.close_time else "N/A",
                trade.status
            )
            
            # Determine tag
            if trade.pnl > 0:
                tag = 'profit'
                wins += 1
            elif trade.pnl < 0:
                tag = 'loss'
                losses += 1
            else:
                tag = 'breakeven'
            
            total_pnl += trade.pnl
            
            item = self.tree.insert('', 'end', values=values, tags=(tag,))
            self.tree.set(item, 'Trade ID', trade.trade_id)  # Store trade_id for reference
        
        # Update statistics
        total = len(paper_trader.closed_trades)
        self.stats_labels['total'].config(text=f"Total: {total}")
        self.stats_labels['wins'].config(text=f"Wins: {wins}")
        self.stats_labels['losses'].config(text=f"Losses: {losses}")
        
        pnl_color = self.colors['profit_green'] if total_pnl >= 0 else self.colors['loss_red']
        self.stats_labels['total_pnl'].config(text=f"Total P&L: ${total_pnl:+.2f}", fg=pnl_color)
        
    def on_click(self, event):
        """Handle click on tree item"""
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return
        
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        
        # Check if clicked on Select column
        if column == '#1' and item:
            trade_id = self.tree.item(item, 'values')[1]
            
            if item in self.selected_trades:
                # Deselect
                self.selected_trades.remove(item)
                self.tree.set(item, 'Select', '☐')
                # Remove selected tag
                tags = list(self.tree.item(item, 'tags'))
                if 'selected' in tags:
                    tags.remove('selected')
                self.tree.item(item, tags=tags)
            else:
                # Select
                self.selected_trades.add(item)
                self.tree.set(item, 'Select', '☑')
                # Add selected tag
                tags = list(self.tree.item(item, 'tags'))
                tags.append('selected')
                self.tree.item(item, tags=tags)
            
            self.selection_label.config(text=f"Selected: {len(self.selected_trades)}")
    
    def select_all(self):
        """Select all visible trades"""
        self.selected_trades.clear()
        for item in self.tree.get_children():
            self.selected_trades.add(item)
            self.tree.set(item, 'Select', '☑')
            tags = list(self.tree.item(item, 'tags'))
            if 'selected' not in tags:
                tags.append('selected')
            self.tree.item(item, tags=tags)
        self.selection_label.config(text=f"Selected: {len(self.selected_trades)}")
    
    def deselect_all(self):
        """Deselect all trades"""
        for item in self.selected_trades:
            self.tree.set(item, 'Select', '☐')
            tags = list(self.tree.item(item, 'tags'))
            if 'selected' in tags:
                tags.remove('selected')
            self.tree.item(item, tags=tags)
        self.selected_trades.clear()
        self.selection_label.config(text=f"Selected: 0")
    
    def delete_selected(self):
        """Delete selected trades after confirmation"""
        if not self.selected_trades:
            messagebox.showwarning("No Selection", "Please select trades to delete.")
            return
        
        count = len(self.selected_trades)
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete {count} trade(s)?\n\nThis action cannot be undone!"
        )
        
        if not response:
            return
        
        # Get trade IDs to delete
        trade_ids_to_delete = []
        for item in self.selected_trades:
            trade_id = self.tree.item(item, 'values')[1]
            trade_ids_to_delete.append(trade_id)
        
        # Delete from paper_trader
        deleted_count = 0
        for trade_id in trade_ids_to_delete:
            # Delete ALL trades with this ID (handles duplicates)
            trades_to_remove = []
            for i, trade in enumerate(paper_trader.closed_trades):
                if trade.trade_id == trade_id:
                    trades_to_remove.append(i)
                    # Subtract P&L from totals
                    paper_trader.total_pnl -= trade.pnl
                    paper_trader.total_commission -= trade.commission * 2
                    
                    # Remove from daily P&L
                    if trade.close_time:
                        day = trade.close_time.date().isoformat()
                        if day in paper_trader.daily_pnl:
                            paper_trader.daily_pnl[day] -= trade.pnl
                    
                    deleted_count += 1
            
            # Delete trades in reverse order to avoid index shifting
            for i in reversed(trades_to_remove):
                del paper_trader.closed_trades[i]
        
        # Save updated state
        paper_trader.save_trades()
        
        # Reload display
        self.load_trades()
        
        messagebox.showinfo("Deleted", f"Successfully deleted {deleted_count} trade(s).")
    
    def apply_filter(self):
        """Apply ticker filter"""
        ticker = self.ticker_filter.get().strip().upper()
        
        if not ticker:
            self.load_trades()
            return
        
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load filtered trades
        for trade in paper_trader.closed_trades:
            if ticker and ticker not in trade.ticker:
                continue
            
            # Calculate duration
            if trade.close_time and trade.open_time:
                duration = trade.close_time - trade.open_time
                duration_str = f"{duration.seconds // 3600}h {(duration.seconds % 3600) // 60}m"
            else:
                duration_str = "N/A"
            
            values = (
                '☐',
                trade.trade_id,
                trade.ticker,
                trade.direction,
                f"{trade.quantity:,}",
                f"${trade.open_price:.2f}",
                f"${trade.close_price:.2f}" if trade.close_price else "N/A",
                f"${trade.pnl:+.2f}",
                f"{trade.pnl_percent:+.2f}%",
                duration_str,
                trade.open_time.strftime("%Y-%m-%d %H:%M:%S"),
                trade.close_time.strftime("%Y-%m-%d %H:%M:%S") if trade.close_time else "N/A",
                trade.status
            )
            
            tag = 'profit' if trade.pnl > 0 else 'loss' if trade.pnl < 0 else 'breakeven'
            self.tree.insert('', 'end', values=values, tags=(tag,))
    
    def clear_filter(self):
        """Clear all filters"""
        self.ticker_filter.delete(0, tk.END)
        self.load_trades()
    
    def sort_column(self, col):
        """Sort tree by column"""
        # Not implemented yet - placeholder for future enhancement
        pass
    
    def export_csv(self):
        """Export trades to CSV"""
        if not paper_trader.closed_trades:
            messagebox.showinfo("No Data", "No trades to export.")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=f"trade_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Trade ID', 'Ticker', 'Direction', 'Quantity', 'Entry Price', 'Exit Price', 
                               'P&L', 'P&L %', 'Open Time', 'Close Time', 'Status'])
                
                for trade in paper_trader.closed_trades:
                    writer.writerow([
                        trade.trade_id,
                        trade.ticker,
                        trade.direction,
                        trade.quantity,
                        trade.open_price,
                        trade.close_price,
                        trade.pnl,
                        trade.pnl_percent,
                        trade.open_time.isoformat(),
                        trade.close_time.isoformat() if trade.close_time else '',
                        trade.status
                    ])
            
            messagebox.showinfo("Export Complete", f"Exported {len(paper_trader.closed_trades)} trades to:\n{filename}")
        
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export:\n{str(e)}")

def open_trade_history_editor():
    """Open the trade history editor window"""
    TradeHistoryEditor()

if __name__ == "__main__":
    # Test standalone
    root = tk.Tk()
    root.withdraw()
    open_trade_history_editor()
    root.mainloop()
