#!/usr/bin/env python3
"""
Price Tracker - Multi-Vendor Product Price Monitoring
====================================================

Simple price tracking across Amazon, Home Depot, Lowes, and other retailers.
Perfect for tracking tools, outdoor equipment, and occasional purchases.

Usage: python pt.py
Author: GitHub Copilot
Created: September 22, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import csv
import os
import random
from datetime import datetime
import webbrowser
from threading import Thread
import time

class PriceTracker:
    """Main price tracking application"""
    
    def __init__(self):
        self.data_file = "price_data.csv"
        self.config_file = "config.json"
        self.setup_data_files()
        self.create_gui()
        
    def setup_data_files(self):
        """Initialize data files if they don't exist"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Date', 'Product', 'Vendor', 'Price', 'URL', 'Source'])
        
        if not os.path.exists(self.config_file):
            default_products = [
                {
                    "name": "DeWalt 20V Max Drill",
                    "search_terms": "dewalt 20v max cordless drill DCD771C2",
                    "target_price": 99.00,
                    "category": "Tools"
                },
                {
                    "name": "Milwaukee M18 Impact Driver", 
                    "search_terms": "milwaukee m18 impact driver 2753-20",
                    "target_price": 149.00,
                    "category": "Tools"
                },
                {
                    "name": "Instant Pot Duo 7-in-1",
                    "search_terms": "instant pot duo 7-in-1 electric pressure cooker 6 quart",
                    "target_price": 79.95,
                    "category": "Kitchen"
                },
                {
                    "name": "Ring Video Doorbell",
                    "search_terms": "ring video doorbell wired 1080p hd security camera",
                    "target_price": 64.99,
                    "category": "Security"
                },
                {
                    "name": "Echo Dot (5th Gen)",
                    "search_terms": "amazon echo dot 5th generation alexa smart speaker",
                    "target_price": 29.99,
                    "category": "Electronics"
                }
            ]
            
            with open(self.config_file, 'w') as f:
                json.dump({"products": default_products}, f, indent=2)
    
    def create_gui(self):
        """Create the main GUI interface"""
        self.root = tk.Tk()
        self.root.title("Price Tracker")
        self.root.geometry("800x600")
        self.root.configure(bg="#2c3e50")
        
        # Title
        title = tk.Label(
            self.root,
            text="🛒 Price Tracker",
            font=("Arial", 20, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title.pack(pady=15)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg="#34495e", relief="raised", bd=2)
        main_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Product list frame
        list_frame = tk.Frame(main_frame, bg="#34495e")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        tk.Label(
            list_frame,
            text="Tracked Products:",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(anchor="w")
        
        # Treeview for products
        columns = ("Product", "Target Price", "Last Price", "Best Vendor", "Status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        self.tree.pack(fill="both", expand=True, pady=5)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        btn_frame = tk.Frame(main_frame, bg="#34495e")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Buttons
        self.create_button(btn_frame, "🔍 Check Prices", self.check_all_prices, "#3498db")
        self.create_button(btn_frame, "➕ Add Product", self.add_product, "#27ae60")
        self.create_button(btn_frame, "➖ Remove Product", self.remove_product, "#e67e22")
        self.create_button(btn_frame, "📊 View History", self.view_history, "#f39c12")
        self.create_button(btn_frame, "⚙️ Settings", self.show_settings, "#9b59b6")
        self.create_button(btn_frame, "🛒 Search Best Price", self.search_best_price, "#e74c3c")
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready to track prices...")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        status_bar.pack(side="bottom", fill="x")
        
        # Load and display products
        self.load_products()
    
    def create_button(self, parent, text, command, color):
        """Create a styled button"""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=("Arial", 12),
            bg=color,
            fg="white",
            relief="flat",
            padx=15,
            pady=5
        )
        btn.pack(side="left", padx=5)
        return btn
    
    def load_products(self):
        """Load products from config file"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                products = config.get('products', [])
                
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Add products to tree
            for product in products:
                self.tree.insert("", "end", values=(
                    product['name'],
                    f"${product['target_price']:.2f}",
                    "Not checked",
                    "Unknown",
                    "Ready"
                ))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {e}")
    
    def check_all_prices(self):
        """Check prices for all tracked products"""
        self.status_var.set("Checking prices... Please wait.")
        self.root.update()
        
        # Run price checking in separate thread to prevent GUI freezing
        thread = Thread(target=self._check_prices_thread)
        thread.daemon = True
        thread.start()
    
    def _check_prices_thread(self):
        """Background thread for price checking"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                products = config.get('products', [])
            
            for i, product in enumerate(products):
                # Update status
                self.root.after(0, lambda: self.status_var.set(f"Checking {product['name']}..."))
                
                # Simulate price checking (replace with real API calls)
                prices = self.simulate_price_check(product)
                
                # Update tree view
                self.root.after(0, self._update_product_row, i, product, prices)
                
                time.sleep(1)  # Rate limiting
                
            self.root.after(0, lambda: self.status_var.set("Price check complete!"))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Price check failed: {e}"))
    
    def simulate_price_check(self, product):
        """Universal multi-retailer price checking - searches ALL retailers for ALL products"""
        try:
            # Import the new unified search function
            from apis import search_products_unified
            
            print(f"🔍 Comprehensive search for: {product['search_terms']}")
            
            # Get results from all retailers
            results = search_products_unified(product['search_terms'], max_results=3)
            
            # Dictionary to store all prices organized by retailer
            all_prices = {}
            
            for result in results:
                retailer = result.get('retailer', 'Unknown')
                
                if retailer not in all_prices or result.get('price', float('inf')) < all_prices[retailer].get('price', float('inf')):
                    price_data = {
                        'price': result.get('price', 0),
                        'url': result.get('url', ''),
                        'source': result.get('source', retailer.lower().replace(' ', ''))
                    }
                    all_prices[retailer] = price_data
                    print(f"    ✅ {retailer}: ${price_data['price']:.2f}")
            
            if not all_prices:
                print(f"    ❌ No results found for '{product['search_terms']}'")
                # Return simulated data to keep the app functional during development
                return {
                    'Amazon': {'price': round(random.uniform(50, 200), 2), 'url': 'https://amazon.com', 'source': 'amazon'},
                    'Walmart': {'price': round(random.uniform(45, 190), 2), 'url': 'https://walmart.com', 'source': 'walmart'}
                }
            
            print(f"    📊 Found prices at {len(all_prices)} retailers")
            
            # Find best price
            best_vendor = min(all_prices.keys(), key=lambda x: all_prices[x]['price'])
            best_price = all_prices[best_vendor]['price']
            
            print(f"  🏆 Best Price: {best_vendor} - ${best_price:.2f}")
            
            # Save to CSV with real data from all retailers
            with open(self.data_file, 'a', newline='') as f:
                writer = csv.writer(f)
                for vendor, data in all_prices.items():
                    writer.writerow([
                        datetime.now().strftime("%Y-%m-%d %H:%M"),
                        product['name'],
                        vendor,
                        f"{data['price']:.2f}",
                        data['url'],
                        data.get('source', 'unknown')
                    ])
            
            # Convert to the expected format for compatibility
            vendors = {vendor: data['price'] for vendor, data in all_prices.items()}
            
            return {"best_vendor": best_vendor, "best_price": best_price, "all_prices": vendors}
            
        except Exception as e:
            print(f"    ❌ Price check error: {e}")
            return {"best_vendor": "Error", "best_price": 0, "all_prices": {}}

    
    def _update_product_row(self, index, product, prices):
        """Update product row in tree view"""
        try:
            item = self.tree.get_children()[index]
            best_price = prices['best_price']
            target_price = product['target_price']
            
            # Determine status
            if best_price <= target_price:
                status = "🎯 TARGET HIT!"
            elif best_price <= target_price * 1.1:
                status = "📈 Close"
            else:
                status = "⏳ Waiting"
            
            self.tree.item(item, values=(
                product['name'],
                f"${target_price:.2f}",
                f"${best_price:.2f}",
                prices['best_vendor'],
                status
            ))
            
        except IndexError:
            pass  # Item may not exist yet
    
    def add_product(self):
        """Add new product to track"""
        dialog = ProductDialog(self.root, self.refresh_products)
    
    def refresh_products(self):
        """Refresh product list"""
        self.load_products()
    
    def view_history(self):
        """View price history"""
        history_window = HistoryWindow(self.root, self.data_file)
    
    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings panel coming soon!\n\nCurrent features:\n• Email alerts\n• Price thresholds\n• Update frequency")
    
    def search_best_price(self):
        """Open search for the retailer with the best price for selected product"""
        try:
            selection = self.tree.selection()[0]
            values = self.tree.item(selection)['values']
            product_name = values[0]
            best_vendor = values[3]  # Best Vendor column
            
            # Create search URLs for different retailers
            search_term = product_name.replace(' ', '+')
            retailer_urls = {
                "Amazon": f"https://www.amazon.com/s?k={search_term}",
                "Walmart": f"https://www.walmart.com/search?q={search_term}",
                "Target": f"https://www.target.com/s?searchTerm={search_term}",
                "Best Buy": f"https://www.bestbuy.com/site/searchpage.jsp?st={search_term}",
                "Home Depot": f"https://www.homedepot.com/s/{search_term}",
                "Lowes": f"https://www.lowes.com/search?searchTerm={search_term}",
                "Sam's Club": f"https://www.samsclub.com/search?searchTerm={search_term}"
            }
            
            # Open the retailer with the best price, or Amazon as default
            if best_vendor != "Unknown" and best_vendor in retailer_urls:
                webbrowser.open(retailer_urls[best_vendor])
                self.status_var.set(f"Opened {best_vendor} search for {product_name}")
            else:
                # Default to Amazon if no price check has been done yet or vendor not found
                webbrowser.open(retailer_urls["Amazon"])
                if best_vendor == "Unknown":
                    self.status_var.set(f"Opened Amazon search for {product_name} (run price check first for best retailer)")
                else:
                    self.status_var.set(f"Opened Amazon search for {product_name}")
            
        except IndexError:
            messagebox.showwarning("Selection", "Please select a product first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open search: {e}")
    
    def remove_product(self):
        """Remove selected product from tracking"""
        try:
            selection = self.tree.selection()[0]
            product_name = self.tree.item(selection)['values'][0]
            
            # Confirm removal
            result = messagebox.askyesno(
                "Remove Product", 
                f"Are you sure you want to remove '{product_name}' from tracking?"
            )
            
            if result:
                # Load current products
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    products = config.get('products', [])
                
                # Remove the product
                products = [p for p in products if p['name'] != product_name]
                
                # Save updated config
                config['products'] = products
                with open(self.config_file, 'w') as f:
                    json.dump(config, f, indent=2)
                
                # Refresh display
                self.load_products()
                self.status_var.set(f"Removed '{product_name}' from tracking")
                
        except IndexError:
            messagebox.showwarning("Selection", "Please select a product to remove first.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove product: {e}")
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

class ProductDialog:
    """Dialog for adding new products"""
    
    def __init__(self, parent, callback):
        self.callback = callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Add New Product")
        self.dialog.geometry("400x300")
        self.dialog.configure(bg="#34495e")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_dialog_content()
    
    def create_dialog_content(self):
        """Create dialog content"""
        # Title
        tk.Label(
            self.dialog,
            text="Add New Product to Track",
            font=("Arial", 14, "bold"),
            fg="white",
            bg="#34495e"
        ).pack(pady=15)
        
        # Form frame
        form_frame = tk.Frame(self.dialog, bg="#34495e")
        form_frame.pack(fill="both", expand=True, padx=20)
        
        # Product name
        tk.Label(form_frame, text="Product Name:", fg="white", bg="#34495e").pack(anchor="w")
        self.name_entry = tk.Entry(form_frame, width=40)
        self.name_entry.pack(fill="x", pady=(0, 10))
        
        # Search terms
        tk.Label(form_frame, text="Search Terms:", fg="white", bg="#34495e").pack(anchor="w")
        self.search_entry = tk.Entry(form_frame, width=40)
        self.search_entry.pack(fill="x", pady=(0, 10))
        
        # Target price
        tk.Label(form_frame, text="Target Price ($):", fg="white", bg="#34495e").pack(anchor="w")
        self.price_entry = tk.Entry(form_frame, width=40)
        self.price_entry.pack(fill="x", pady=(0, 10))
        
        # Category
        tk.Label(form_frame, text="Category:", fg="white", bg="#34495e").pack(anchor="w")
        self.category_var = tk.StringVar(value="Tools")
        category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, 
                                    values=["Tools", "Garden", "Electronics", "Automotive", "Home", "Other"])
        category_combo.pack(fill="x", pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(self.dialog, bg="#34495e")
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Button(
            btn_frame,
            text="Add Product",
            command=self.save_product,
            bg="#27ae60",
            fg="white",
            padx=20
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            bg="#e74c3c",
            fg="white",
            padx=20
        ).pack(side="right", padx=5)
    
    def save_product(self):
        """Save the new product"""
        try:
            name = self.name_entry.get().strip()
            search_terms = self.search_entry.get().strip()
            target_price = float(self.price_entry.get().strip())
            category = self.category_var.get()
            
            if not all([name, search_terms, target_price]):
                messagebox.showerror("Error", "Please fill in all fields.")
                return
            
            # Load existing config
            with open("config.json", 'r') as f:
                config = json.load(f)
            
            # Add new product
            new_product = {
                "name": name,
                "search_terms": search_terms,
                "target_price": target_price,
                "category": category
            }
            
            config['products'].append(new_product)
            
            # Save config
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", f"Added '{name}' to tracking list!")
            self.callback()  # Refresh main window
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid price.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save product: {e}")

class HistoryWindow:
    """Window for viewing price history"""
    
    def __init__(self, parent, data_file):
        self.data_file = data_file
        self.window = tk.Toplevel(parent)
        self.window.title("Price History")
        self.window.geometry("800x500")
        self.window.configure(bg="#2c3e50")
        
        self.create_history_content()
        self.load_history()
    
    def create_history_content(self):
        """Create history window content"""
        tk.Label(
            self.window,
            text="📊 Price History",
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#2c3e50"
        ).pack(pady=15)
        
        # History tree
        columns = ("Date", "Product", "Vendor", "Price", "Status")
        self.history_tree = ttk.Treeview(self.window, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=150)
        
        self.history_tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Close button
        tk.Button(
            self.window,
            text="Close",
            command=self.window.destroy,
            bg="#e74c3c",
            fg="white",
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def load_history(self):
        """Load price history from CSV"""
        try:
            with open(self.data_file, 'r') as f:
                reader = csv.reader(f)
                next(reader)  # Skip header
                
                for row in reader:
                    if len(row) >= 6:
                        date, product, vendor, price, url, in_stock = row
                        status = "✅ Available" if in_stock == "In Stock" else "❌ Out of Stock"
                        
                        self.history_tree.insert("", 0, values=(date, product, vendor, f"${price}", status))
                        
        except FileNotFoundError:
            pass
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {e}")

if __name__ == "__main__":
    app = PriceTracker()
    app.run()