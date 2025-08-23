"""
Ticker Manager GUI
------------------
A simple Tkinter-based popup interface for adding, viewing, and removing tickers from the watchlist.
Integrates with utils.watchlist_manager and models.instrument.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

import os
import sys
# Ensure project root is in sys.path for absolute imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from wishlist_tracker.utils.watchlist_manager import load_watchlist, save_watchlist
from wishlist_tracker.models.instrument import Instrument

WATCHLIST_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'watchlist.csv')


class TickerManagerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Ticker Manager")
        master.geometry("600x500")
        master.configure(bg="#e3f0ff")  # Light blue background

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#b8c1ec",  # Light blue rows
                        foreground="#232946",
                        rowheight=25,
                        fieldbackground="#b8c1ec",
                        font=("Segoe UI", 11))
        style.configure("Treeview.Heading",
                        background="#232946",
                        foreground="#b8c1ec",
                        font=("Segoe UI", 12, "bold"))
        style.map('Treeview', background=[('selected', '#a3cef1')])

        entry_frame = tk.Frame(master, bg="#e3f0ff")
        entry_frame.pack(pady=10)

        self.ticker_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.notes_var = tk.StringVar()

        tk.Label(entry_frame, text="Ticker Symbol:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e")
        tk.Entry(entry_frame, textvariable=self.ticker_var, font=("Segoe UI", 11)).grid(row=0, column=1, padx=5)
        tk.Label(entry_frame, text="Name:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e")
        tk.Entry(entry_frame, textvariable=self.name_var, font=("Segoe UI", 11)).grid(row=1, column=1, padx=5)
        tk.Label(entry_frame, text="Notes:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e")
        tk.Entry(entry_frame, textvariable=self.notes_var, font=("Segoe UI", 11)).grid(row=2, column=1, padx=5)

        btn_frame = tk.Frame(master, bg="#e3f0ff")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Add Ticker", command=self.add_ticker, bg="#a3cef1", fg="#232946", font=("Segoe UI", 11, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_selected, bg="#b8c1ec", fg="#232946", font=("Segoe UI", 11, "bold"), width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.remove_selected, bg="#f44336", fg="#fff", font=("Segoe UI", 11, "bold"), width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.refresh_watchlist, bg="#232946", fg="#b8c1ec", font=("Segoe UI", 11), width=10).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(master, columns=("Symbol", "Name", "Notes"), show="headings", selectmode="browse")
        self.tree.heading("Symbol", text="Symbol")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Notes", text="Notes")
        self.tree.pack(expand=True, fill=tk.BOTH, pady=10, padx=10)

        self.tree.bind("<Double-1>", self.on_tree_double_click)

        self.refresh_watchlist()

    def add_ticker(self):
        symbol = self.ticker_var.get().strip().upper()
        name = self.name_var.get().strip()
        notes = self.notes_var.get().strip()
        if not symbol:
            messagebox.showerror("Input Error", "Ticker symbol is required.")
            return
        watchlist = load_watchlist(WATCHLIST_CSV)
        if any(inst.symbol == symbol for inst in watchlist):
            messagebox.showwarning("Duplicate", f"Ticker '{symbol}' is already in the watchlist.")
            return
        inst = Instrument(symbol=symbol, name=name, notes=notes)
        watchlist.append(inst)
        save_watchlist(watchlist, WATCHLIST_CSV)
        self.refresh_watchlist()
        self.ticker_var.set("")
        self.name_var.set("")
        self.notes_var.set("")

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a ticker to edit.")
            return
        item = self.tree.item(selected[0])
        symbol, name, notes = item['values']
        # Pop up dialog to edit fields
        edit_win = tk.Toplevel(self.master)
        edit_win.title(f"Edit Ticker: {symbol}")
        edit_win.configure(bg="#e3f0ff")
        tk.Label(edit_win, text="Symbol:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="e")
        symbol_var = tk.StringVar(value=symbol)
        tk.Entry(edit_win, textvariable=symbol_var, font=("Segoe UI", 11)).grid(row=0, column=1, padx=5)
        tk.Label(edit_win, text="Name:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="e")
        name_var = tk.StringVar(value=name)
        tk.Entry(edit_win, textvariable=name_var, font=("Segoe UI", 11)).grid(row=1, column=1, padx=5)
        tk.Label(edit_win, text="Notes:", bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="e")
        notes_var = tk.StringVar(value=notes)
        tk.Entry(edit_win, textvariable=notes_var, font=("Segoe UI", 11)).grid(row=2, column=1, padx=5)

        def save_edits():
            new_symbol = symbol_var.get().strip().upper()
            new_name = name_var.get().strip()
            new_notes = notes_var.get().strip()
            if not new_symbol:
                messagebox.showerror("Input Error", "Ticker symbol is required.")
                return
            watchlist = load_watchlist(WATCHLIST_CSV)
            # Remove old, add new (handle symbol change)
            new_watchlist = []
            found = False
            for inst in watchlist:
                if inst.symbol == symbol:
                    found = True
                    new_watchlist.append(Instrument(symbol=new_symbol, name=new_name, notes=new_notes))
                else:
                    new_watchlist.append(inst)
            if not found:
                messagebox.showerror("Error", "Ticker not found in watchlist.")
                edit_win.destroy()
                return
            save_watchlist(new_watchlist, WATCHLIST_CSV)
            self.refresh_watchlist()
            edit_win.destroy()

        tk.Button(edit_win, text="Save", command=save_edits, bg="#a3cef1", fg="#232946", font=("Segoe UI", 11, "bold"), width=10).grid(row=3, column=0, pady=10)
        tk.Button(edit_win, text="Cancel", command=edit_win.destroy, bg="#e3f0ff", fg="#232946", font=("Segoe UI", 11), width=10).grid(row=3, column=1, pady=10)

    def on_tree_double_click(self, event):
        self.edit_selected()

    def remove_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No Selection", "Please select a ticker to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected ticker?")
        if not confirm:
            return
        watchlist = load_watchlist(WATCHLIST_CSV)
        symbols_to_remove = [self.tree.item(item, 'values')[0] for item in selected]
        new_watchlist = [inst for inst in watchlist if inst.symbol not in symbols_to_remove]
        save_watchlist(new_watchlist, WATCHLIST_CSV)
        self.refresh_watchlist()

    def refresh_watchlist(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        watchlist = load_watchlist(WATCHLIST_CSV)
        for inst in watchlist:
            self.tree.insert('', 'end', values=(inst.symbol, inst.name, inst.notes))

if __name__ == "__main__":
    root = tk.Tk()
    app = TickerManagerGUI(root)
    root.mainloop()
