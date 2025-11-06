"""
Simple TreeView Test for Windows Display Issues
==============================================

This test creates the simplest possible TreeView to verify Windows compatibility
and help diagnose the Live Dashboard display issue.

Author: GitHub Copilot
Date: October 3, 2025
"""

import tkinter as tk
from tkinter import ttk
import time

def test_simple_treeview():
    """Test very basic TreeView functionality"""
    print("🧪 Starting simple TreeView test...")
    
    # Create root window
    root = tk.Tk()
    root.title("Simple TreeView Test")
    root.geometry("800x600")
    
    # Configure style for proper emoji and color support
    style = ttk.Style()
    # Use font stack that includes good emoji support for Windows
    emoji_font = ("Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Arial Unicode MS", 12)
    style.configure("Treeview", font=emoji_font, rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    
    # Create TreeView with same columns as Live Dashboard
    columns = ("Symbol", "Company", "Score", "Direction", "Confidence", "Price Change", "Volume", "Alert")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
    
    # Configure color tags for different alert levels
    tree.tag_configure("good", foreground="darkgreen", background="lightgreen")
    tree.tag_configure("watch", foreground="darkorange", background="lightyellow")
    tree.tag_configure("alert", foreground="darkred", background="lightpink")
    tree.tag_configure("neutral", foreground="black", background="white")
    
    # Configure headers
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    
    # Pack directly into root (no containers)
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Add very obvious test data with color tags
    test_data = [
        ("TEST1", "FIRST ITEM", "9.5", "Up", "95%", "+5.2%", "+25%", "Good"),
        ("TEST2", "SECOND ITEM", "8.3", "Down", "87%", "-2.1%", "+10%", "Watch"),
        ("AAPL", "Apple Inc", "7.8", "Up", "82%", "+1.5%", "+15%", "Good"),
        ("MSFT", "Microsoft", "8.9", "Up", "91%", "+2.3%", "+20%", "Good"),
    ]
    
    print("🔧 Adding data to TreeView...")
    for i, data in enumerate(test_data):
        # Add without tags first to test basic functionality
        item_id = tree.insert("", "end", values=data)
        print(f"✅ Added item {i+1}: {data[0]} -> {item_id}")
        
        # Force individual update after each insert
        tree.update()
        tree.see(item_id)  # Ensure item is visible
    
    # Force comprehensive updates
    print("🔧 Forcing TreeView updates...")
    tree.update_idletasks()
    tree.update()
    root.update_idletasks()
    root.update()
    
    # Verify items exist in TreeView
    children = tree.get_children()
    print(f"🔍 TreeView reports {len(children)} items:")
    for i, child in enumerate(children):
        item_data = tree.item(child)
        values = item_data.get('values', [])
        if values:
            print(f"   📊 Item {i+1}: {values[0]} | {values[1]} | Score: {values[2]}")
        else:
            print(f"   ❌ Item {i+1}: No values found!")
    
    # Final verification - try to select items to make them visible
    if children:
        tree.selection_set(children[0])  # Select first item
        tree.focus(children[0])          # Focus on first item
    
    print("\n🚀 Simple TreeView test window opened!")
    print("   - TreeView should now show data properly")
    print("   - Check if you can see the 4 test items")
    print("   - Close window when done testing")
    
    root.mainloop()

def test_complex_layout():
    """Test TreeView in containers similar to Live Dashboard"""
    print("🧪 Starting complex layout test...")
    
    # Create root window
    root = tk.Tk()
    root.title("Complex TreeView Test")
    root.geometry("900x700")
    
    # Configure style for proper emoji and color support
    style = ttk.Style()
    emoji_font = ("Segoe UI Emoji", "Apple Color Emoji", "Noto Color Emoji", "Arial Unicode MS", 12)
    style.configure("Treeview", font=emoji_font, rowheight=25)
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"))
    
    # Create container structure similar to Live Dashboard
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create labeled frame
    table_frame = ttk.LabelFrame(main_frame, text="🎯 Test Catalyst Scores", padding=5)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Create TreeView
    columns = ("Symbol", "Company", "Score", "Direction", "Confidence", "Price Change", "Volume", "Alert")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
    
    # Configure color tags
    tree.tag_configure("excellent", foreground="darkgreen", background="lightgreen")
    tree.tag_configure("good", foreground="green", background="white")
    tree.tag_configure("watch", foreground="darkorange", background="lightyellow")
    tree.tag_configure("alert", foreground="darkred", background="lightpink")
    tree.tag_configure("neutral", foreground="black", background="white")
    
    # Configure columns
    column_configs = {
        "Symbol": 80,
        "Company": 150,
        "Score": 80,
        "Direction": 120,
        "Confidence": 100,
        "Price Change": 100,
        "Volume": 100,
        "Alert": 140
    }
    
    for col, width in column_configs.items():
        tree.heading(col, text=col)
        tree.column(col, width=width, minwidth=50)
    
    # Pack TreeView
    tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    scrollbar.pack(side='right', fill='y')
    tree.configure(yscrollcommand=scrollbar.set)
    
    # Add test data with colors
    test_data = [
        (("VISIBLE", "🔥 CAN YOU SEE?", "10.0", "🚀 Up", "100%", "+99%", "+99%", "🟢 WORKING"), "excellent"),
        (("TEST", "📊 DISPLAY CHECK", "9.5", "↗️ Bullish", "95%", "+5.2%", "+25%", "🟢 Good"), "good"),
        (("AAPL", "Apple Inc", "8.7", "↗️ Up", "89%", "+2.1%", "+18%", "🟢 Good"), "good"),
        (("MSFT", "Microsoft", "8.9", "↗️ Up", "91%", "+2.3%", "+20%", "🟢 Good"), "good"),
        (("GOOGL", "Alphabet", "7.5", "↔️ Neutral", "78%", "+0.5%", "+8%", "🟡 Watch"), "watch")
    ]
    
    for data, tag in test_data:
        item_id = tree.insert("", "end", values=data, tags=(tag,))
        print(f"✅ Added: {data[0]} -> {item_id} with tag '{tag}'")
    
    # Force updates
    tree.update_idletasks()
    table_frame.update_idletasks()
    main_frame.update_idletasks()
    root.update_idletasks()
    
    # Verify items
    children = tree.get_children()
    print(f"🔍 Complex TreeView has {len(children)} items:")
    for child in children:
        values = tree.item(child)['values']
        print(f"   📊 {values[0]}: {values[1]}")
    
    print("\n🚀 Complex TreeView test window opened!")
    print("   - This mimics the Live Dashboard layout structure")
    print("   - Can you see the 5 test items with emojis?")
    print("   - Close window when done testing")
    
    root.mainloop()

if __name__ == "__main__":
    print("🧪 TreeView Windows Compatibility Test")
    print("=" * 50)
    
    print("\n1. Testing simple TreeView (direct to root)...")
    test_simple_treeview()
    
    print("\n2. Testing complex layout (containers like Live Dashboard)...")
    test_complex_layout()
    
    print("\n✅ TreeView tests completed!")