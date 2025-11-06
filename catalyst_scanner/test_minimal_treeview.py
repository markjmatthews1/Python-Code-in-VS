"""
Minimal TreeView Test - Debug Windows Display Issue
=================================================

This is a minimal test to identify why TreeView data isn't displaying on Windows.

Author: GitHub Copilot
Date: October 3, 2025
"""

import tkinter as tk
from tkinter import ttk

def minimal_test():
    """Absolute minimal TreeView test"""
    print("🧪 Starting MINIMAL TreeView test...")
    
    # Create window
    root = tk.Tk()
    root.title("MINIMAL TreeView Test")
    root.geometry("600x400")
    
    # Create TreeView with just 2 columns
    tree = ttk.Treeview(root, columns=("col1", "col2"), show="tree headings")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Set headers
    tree.heading("#0", text="ID")
    tree.heading("col1", text="Name")
    tree.heading("col2", text="Value")
    
    # Set column widths
    tree.column("#0", width=50)
    tree.column("col1", width=150)
    tree.column("col2", width=100)
    
    print("🔧 Adding simple data...")
    
    # Add simple data - no emojis, no colors
    simple_data = [
        ("Item 1", "100"),
        ("Item 2", "200"),  
        ("Item 3", "300"),
        ("VISIBLE TEST", "999")
    ]
    
    for i, (name, value) in enumerate(simple_data):
        item_id = tree.insert("", "end", text=f"#{i+1}", values=(name, value))
        print(f"✅ Added: {name} -> {item_id}")
    
    # Force updates
    tree.update()
    root.update()
    
    # Check what's in the tree
    children = tree.get_children()
    print(f"\n🔍 TreeView has {len(children)} children:")
    for child in children:
        item = tree.item(child)
        text = item.get('text', '')
        values = item.get('values', [])
        print(f"   📊 {text}: {values}")
    
    print(f"\n🚀 MINIMAL test window opened!")
    print("   - Can you see 4 simple items with no formatting?")
    print("   - This tests basic TreeView functionality")
    
    root.mainloop()

if __name__ == "__main__":
    minimal_test()