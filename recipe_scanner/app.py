"""
Recipe Scanner Pro - Main Application
A standalone desktop app for recipe scanning and management
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import sys
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageTk
from database.db_manager import DatabaseManager
from scanner.scanner_interface import ScannerInterface
from ocr.ocr_engine import OCREngine
from matcher.ingredient_matcher import IngredientMatcher

# Set appearance mode and color theme
ctk.set_appearance_mode("light")  # "light" or "dark"
ctk.set_default_color_theme("green")  # "blue", "green", "dark-blue"

class RecipeScannerApp(ctk.CTk):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("🍳 Recipe Scanner Pro")
        self.geometry("1200x800")
        self.minsize(1000, 600)
        
        # Initialize data directory
        self.setup_directories()
        
        # Initialize database connection
        self.db_path = Path("data/recipes.db")
        self.db = DatabaseManager(str(self.db_path))
        
        # Initialize scanner
        self.scanner = ScannerInterface()
        self.current_scanned_image = None
        self.scanned_pages = []  # For multi-page recipes
        self.combined_ocr_text = ""  # Combined text from multiple pages
        
        # Initialize OCR
        self.ocr = OCREngine()
        
        # Initialize ingredient matcher
        self.matcher = IngredientMatcher(self.db)
        self.available_ingredients = []
        
        # Color scheme
        self.colors = {
            'primary': '#2ECC71',      # Green
            'secondary': '#3498DB',    # Blue
            'accent': '#E74C3C',       # Red
            'success': '#27AE60',      # Dark Green
            'warning': '#F39C12',      # Orange
            'error': '#E74C3C',        # Red (for delete buttons)
            'bg_light': '#ECF0F1',     # Light Gray
            'bg_dark': '#2C3E50',      # Dark Blue-Gray
            'text_dark': '#2C3E50',    # Dark text
            'text_light': '#ECF0F1',   # Light text
            'card_bg': '#FFFFFF',      # White
            'button_bg': '#3498DB',    # Blue (for buttons)
            'button_hover': '#2980B9', # Darker Blue (for hover)
            'input_bg': '#FFFFFF',     # White (for inputs)
        }
        
        # Recipe categories (used in dropdowns and filters)
        self.category_options = ["Appetizer", "Main Course", "Dessert", "Breakfast", "Breads & Rolls", "Soup", "Salad", "Side Dish", "Sauces & Dips", "Beverage", "Snack"]
        self.filter_categories = ["All"] + self.category_options  # Browse tab includes "All"
        
        # Create UI components
        self.create_header()
        self.create_navigation()
        self.create_content_area()
        self.create_footer()
        
        # Show home tab by default
        self.show_home_tab()
        
        # Update statistics
        self.update_recipe_count()
        
        # Status bar message
        self.update_status("Ready")
    
    def setup_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            'data',
            'data/scanned_images',
            'data/backups',
            'config'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def create_header(self):
        """Create application header"""
        self.header_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color=self.colors['primary'])
        self.header_frame.pack(fill="x", padx=0, pady=0)
        self.header_frame.pack_propagate(False)
        
        # App title
        title_label = ctk.CTkLabel(
            self.header_frame,
            text="🍳 Recipe Scanner Pro",
            font=("Helvetica", 28, "bold"),
            text_color="white"
        )
        title_label.pack(side="left", padx=20, pady=20)
        
        # Recipe count badge
        self.recipe_count_label = ctk.CTkLabel(
            self.header_frame,
            text="📚 0 Recipes",
            font=("Helvetica", 16),
            text_color="white"
        )
        self.recipe_count_label.pack(side="right", padx=20)
    
    def create_navigation(self):
        """Create tab navigation bar"""
        self.nav_frame = ctk.CTkFrame(self, height=60, corner_radius=0, fg_color=self.colors['bg_light'])
        self.nav_frame.pack(fill="x", padx=0, pady=0)
        self.nav_frame.pack_propagate(False)
        
        # Navigation buttons
        nav_buttons = [
            ("🏠 Home", self.show_home_tab),
            ("📷 Scan", self.show_scan_tab),
            ("📖 Browse", self.show_browse_tab),
            ("🔎 Match", self.show_match_tab),
            ("📝 List", self.show_list_tab),
        ]
        
        for text, command in nav_buttons:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                font=("Helvetica", 16, "bold"),
                width=140,
                height=40,
                corner_radius=10,
                command=command,
                fg_color=self.colors['secondary'],
                hover_color=self.colors['primary']
            )
            btn.pack(side="left", padx=10, pady=10)
    
    def create_content_area(self):
        """Create main content area"""
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=self.colors['bg_light'])
        self.content_frame.pack(fill="both", expand=True, padx=0, pady=0)
    
    def create_footer(self):
        """Create status bar footer"""
        self.footer_frame = ctk.CTkFrame(self, height=40, corner_radius=0, fg_color=self.colors['bg_dark'])
        self.footer_frame.pack(fill="x", padx=0, pady=0)
        self.footer_frame.pack_propagate(False)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.footer_frame,
            text="Status: Ready",
            font=("Helvetica", 12),
            text_color=self.colors['text_light']
        )
        self.status_label.pack(side="left", padx=20)
        
        # Theme toggle button
        self.theme_toggle = ctk.CTkButton(
            self.footer_frame,
            text="🌓",
            width=40,
            height=30,
            font=("Helvetica", 16),
            command=self.toggle_theme,
            fg_color=self.colors['secondary']
        )
        self.theme_toggle.pack(side="right", padx=20, pady=5)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            self.footer_frame,
            text="⚙️ Settings",
            width=100,
            height=30,
            font=("Helvetica", 12),
            command=self.show_settings,
            fg_color=self.colors['secondary']
        )
        settings_btn.pack(side="right", padx=5, pady=5)
    
    def clear_content(self):
        """Clear the content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        # Force geometry update to reset layout
        self.content_frame.update_idletasks()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.configure(text=f"Status: {message}")
    
    def update_recipe_count(self):
        """Update recipe count in header"""
        try:
            stats = self.db.get_statistics()
            count = stats.get('total_recipes', 0)
            self.recipe_count_label.configure(text=f"📚 {count} Recipes")
        except Exception as e:
            print(f"Error updating recipe count: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current = ctk.get_appearance_mode()
        new_mode = "dark" if current == "Light" else "light"
        ctk.set_appearance_mode(new_mode)
        self.update_status(f"Theme changed to {new_mode}")
    
    # ========== TAB VIEWS ==========
    
    def show_home_tab(self):
        """Display home/dashboard tab"""
        self.clear_content()
        self.update_status("Home")
        
        # Welcome message
        welcome_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors['card_bg'], corner_radius=15)
        welcome_frame.pack(fill="x", padx=40, pady=30)
        
        welcome_label = ctk.CTkLabel(
            welcome_frame,
            text="👋 Welcome to Recipe Scanner Pro!",
            font=("Helvetica", 32, "bold"),
            text_color=self.colors['primary']
        )
        welcome_label.pack(pady=30)
        
        subtitle = ctk.CTkLabel(
            welcome_frame,
            text="Organize, scan, and discover recipes with ease",
            font=("Helvetica", 18),
            text_color=self.colors['text_dark']
        )
        subtitle.pack(pady=(0, 30))
        
        # Quick stats - Get real data from database
        db_stats = self.db.get_statistics()
        
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", padx=40, pady=10)
        
        stats = [
            ("📚 Total Recipes", str(db_stats.get('total_recipes', 0)), self.colors['primary']),
            ("� Added This Week", str(db_stats.get('added_this_week', 0)), self.colors['secondary']),
            ("⭐ Favorites", str(db_stats.get('favorites', 0)), self.colors['warning']),
            ("🏷️ Total Tags", str(db_stats.get('total_tags', 0)), self.colors['accent'])
        ]
        
        for title, value, color in stats:
            stat_card = ctk.CTkFrame(stats_frame, fg_color=color, corner_radius=10)
            stat_card.pack(side="left", fill="both", expand=True, padx=10)
            
            value_label = ctk.CTkLabel(
                stat_card,
                text=value,
                font=("Helvetica", 36, "bold"),
                text_color="white"
            )
            value_label.pack(pady=(20, 5))
            
            title_label = ctk.CTkLabel(
                stat_card,
                text=title,
                font=("Helvetica", 16),
                text_color="white"
            )
            title_label.pack(pady=(0, 20))
        
        # Quick actions
        actions_frame = ctk.CTkFrame(self.content_frame, fg_color=self.colors['card_bg'], corner_radius=15)
        actions_frame.pack(fill="both", expand=True, padx=40, pady=20)
        
        actions_label = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=("Helvetica", 22, "bold"),
            text_color=self.colors['text_dark']
        )
        actions_label.pack(pady=20)
        
        actions_container = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_container.pack(pady=10)
        
        # Action buttons - Row 1
        scan_btn = ctk.CTkButton(
            actions_container,
            text="📷 Scan New Recipe",
            font=("Helvetica", 16, "bold"),
            width=250,
            height=60,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=self.show_scan_tab
        )
        scan_btn.pack(side="left", padx=10)
        
        manual_btn = ctk.CTkButton(
            actions_container,
            text="✍️ Add Recipe Manually",
            font=("Helvetica", 16, "bold"),
            width=250,
            height=60,
            corner_radius=10,
            fg_color=self.colors['accent'],
            hover_color="#C0392B",
            command=self.show_manual_entry
        )
        manual_btn.pack(side="left", padx=10)
        
        browse_btn = ctk.CTkButton(
            actions_container,
            text="📖 Browse Recipes",
            font=("Helvetica", 16, "bold"),
            width=250,
            height=60,
            corner_radius=10,
            fg_color=self.colors['secondary'],
            command=self.show_browse_tab
        )
        browse_btn.pack(side="left", padx=10)
        
        match_btn = ctk.CTkButton(
            actions_container,
            text="🔎 Find by Ingredients",
            font=("Helvetica", 16, "bold"),
            width=250,
            height=60,
            corner_radius=10,
            fg_color=self.colors['warning'],
            command=self.show_match_tab
        )
        match_btn.pack(side="left", padx=10)
    
    def show_scan_tab(self):
        """Display scanner tab"""
        self.clear_content()
        self.update_status("Scan Mode")
        
        # Create scrollable container
        scroll_container = ctk.CTkScrollableFrame(self.content_frame, fg_color=self.colors['bg_light'])
        scroll_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            scroll_container,
            text="📷 Scan Recipe",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(pady=20)
        
        # Check scanner availability
        if not self.scanner.is_available():
            error_frame = ctk.CTkFrame(scroll_container, fg_color=self.colors['accent'], corner_radius=15)
            error_frame.pack(pady=20, padx=40, fill="x")
            
            error_label = ctk.CTkLabel(
                error_frame,
                text="⚠️ Scanner Not Available\n\nScanner functionality requires pywin32.\nPlease ensure it's installed and your scanner is connected.",
                font=("Helvetica", 14),
                text_color="white",
                justify="center"
            )
            error_label.pack(pady=20)
        
        # Scanner info
        scanners = self.scanner.get_scanners()
        if scanners:
            info_text = f"✅ Found {len(scanners)} scanner(s): {', '.join(scanners)}"
            info_color = self.colors['success']
        else:
            info_text = "🔍 No scanners detected - Make sure scanner is connected and powered on"
            info_color = self.colors['warning']
        
        info_label = ctk.CTkLabel(
            scroll_container,
            text=info_text,
            font=("Helvetica", 14),
            text_color=info_color
        )
        info_label.pack(pady=10)
        
        # Preview area
        self.preview_frame = ctk.CTkFrame(scroll_container, width=700, height=400, fg_color=self.colors['card_bg'], corner_radius=15)
        self.preview_frame.pack(pady=20)
        self.preview_frame.pack_propagate(False)
        
        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text="Scanner Preview\n\n📄\n\nPlace recipe on scanner glass\nand click a button below",
            font=("Helvetica", 18),
            text_color=self.colors['text_dark']
        )
        self.preview_label.pack(expand=True)
        
        # Button container
        button_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        button_frame.pack(pady=20)
        
        # Scan button (with dialog - easier for users)
        scan_dialog_btn = ctk.CTkButton(
            button_frame,
            text="🚀 Start Scan (Windows Dialog)",
            font=("Helvetica", 16, "bold"),
            width=250,
            height=50,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=self.start_scan_dialog
        )
        scan_dialog_btn.pack(side="left", padx=10)
        
        # Import image button
        import_btn = ctk.CTkButton(
            button_frame,
            text="📁 Import Image File",
            font=("Helvetica", 16, "bold"),
            width=220,
            height=50,
            corner_radius=10,
            fg_color=self.colors['secondary'],
            command=self.import_image
        )
        import_btn.pack(side="left", padx=10)
        
        # Process button (only show if image is scanned)
        if self.current_scanned_image:
            # Show page count if multi-page
            page_count = len(self.scanned_pages) + 1  # +1 for current page
            if page_count > 1:
                page_label = ctk.CTkLabel(
                    scroll_container,
                    text=f"📄 {page_count} pages scanned",
                    font=("Helvetica", 14, "bold"),
                    text_color=self.colors['success']
                )
                page_label.pack(pady=10)
            
            # Scan additional page button
            scan_next_btn = ctk.CTkButton(
                button_frame,
                text="➕ Scan Next Page",
                font=("Helvetica", 16, "bold"),
                width=200,
                height=50,
                corner_radius=10,
                fg_color=self.colors['secondary'],
                command=self.scan_next_page
            )
            scan_next_btn.pack(side="left", padx=10)
            
            process_btn = ctk.CTkButton(
                button_frame,
                text="▶️ Process with OCR",
                font=("Helvetica", 16, "bold"),
                width=220,
                height=50,
                corner_radius=10,
                fg_color=self.colors['warning'],
                command=self.process_scanned_image
            )
            process_btn.pack(side="left", padx=10)
        
        # Instructions
        instructions = ctk.CTkLabel(
            scroll_container,
            text="💡 Tip: Ensure recipe is flat on scanner glass for best OCR results\n📸 Alternatively, import an existing image file from your computer",
            font=("Helvetica", 12),
            text_color=self.colors['text_dark'],
            justify="center"
        )
        instructions.pack(pady=20)
    
    def show_browse_tab(self):
        """Display recipe browser tab"""
        self.clear_content()
        self.update_status("Browse Recipes")
        
        # Store current filter state
        if not hasattr(self, 'browse_search_text'):
            self.browse_search_text = ""
        if not hasattr(self, 'browse_category_filter'):
            self.browse_category_filter = "All"
        
        # Title and search
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=40, pady=20)
        
        title = ctk.CTkLabel(
            header_frame,
            text="📖 Browse Recipes",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(side="left")
        
        # Search section with label
        search_container = ctk.CTkFrame(header_frame, fg_color="transparent")
        search_container.pack(side="right", padx=10)
        
        search_label = ctk.CTkLabel(
            search_container,
            text="Search Recipes:",
            font=("Helvetica", 14, "bold"),
            text_color=self.colors['text_dark']
        )
        search_label.pack(anchor="e", pady=(0, 5))
        
        search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Type to search...",
            width=300,
            height=40,
            font=("Helvetica", 16)
        )
        search_entry.insert(0, self.browse_search_text)
        search_entry.pack()
        
        # Bind search to filter recipes
        def on_search_change(*args):
            self.browse_search_text = search_entry.get()
            self.refresh_recipe_grid()
        
        search_entry.bind('<KeyRelease>', on_search_change)
        
        # Main content area
        content = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=40, pady=10)
        
        # Sidebar filters (scrollable to show all categories)
        sidebar = ctk.CTkScrollableFrame(content, width=220, fg_color=self.colors['card_bg'], corner_radius=15)
        sidebar.pack(side="left", fill="y", padx=(0, 20))
        
        sidebar_title = ctk.CTkLabel(
            sidebar,
            text="Filters",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['primary']
        )
        sidebar_title.pack(pady=20)
        
        # Category filters
        for cat in self.filter_categories:
            # Determine if this category is selected
            is_selected = (cat == self.browse_category_filter)
            
            btn = ctk.CTkButton(
                sidebar,
                text=cat,
                width=200,
                height=35,
                corner_radius=8,
                fg_color=self.colors['primary'] if is_selected else "transparent",
                text_color="white" if is_selected else self.colors['text_dark'],
                hover_color=self.colors['success'] if is_selected else self.colors['bg_light'],
                anchor="w",
                command=lambda c=cat: self.filter_by_category(c)
            )
            btn.pack(pady=5, padx=10)
        
        # Recipe grid (scrollable frame to hold recipe cards)
        self.recipe_grid_frame = ctk.CTkScrollableFrame(content, fg_color=self.colors['bg_light'], corner_radius=15)
        self.recipe_grid_frame.pack(side="left", fill="both", expand=True)
        
        # Display recipes with current filters
        self.refresh_recipe_grid()
    
    def filter_by_category(self, category):
        """Filter recipes by category"""
        self.browse_category_filter = category
        self.show_browse_tab()  # Refresh the entire tab
    
    def refresh_recipe_grid(self):
        """Refresh the recipe grid with current filters"""
        # Clear existing recipe cards
        for widget in self.recipe_grid_frame.winfo_children():
            widget.destroy()
        
        # Get filtered recipes
        search_term = self.browse_search_text.strip().lower()
        category = self.browse_category_filter if self.browse_category_filter != "All" else None
        
        recipes = self.db.get_all_recipes(search=search_term if search_term else None, category=category)
        
        if not recipes:
            # Placeholder for no recipes
            no_recipes = ctk.CTkLabel(
                self.recipe_grid_frame,
                text="📭\n\nNo recipes found!\n\nTry adjusting your search or filters.",
                font=("Helvetica", 18),
                text_color=self.colors['text_dark']
            )
            no_recipes.pack(pady=100)
        else:
            # Display recipes
            for recipe in recipes:
                recipe_card = self.create_recipe_card(self.recipe_grid_frame, recipe)
                recipe_card.pack(fill="x", padx=10, pady=5)
    
    def show_match_tab(self):
        """Display ingredient matcher tab"""
        self.clear_content()
        self.update_status("Ingredient Matcher")
        
        # Create scrollable container
        scroll_container = ctk.CTkScrollableFrame(self.content_frame, fg_color=self.colors['bg_light'])
        scroll_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            scroll_container,
            text="🔎 Find Recipes by Ingredients",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(pady=20)
        
        # Input area
        input_frame = ctk.CTkFrame(scroll_container, fg_color=self.colors['card_bg'], corner_radius=15)
        input_frame.pack(fill="x", padx=20, pady=10)
        
        input_label = ctk.CTkLabel(
            input_frame,
            text="What ingredients do you have?",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['text_dark']
        )
        input_label.pack(pady=20)
        
        entry_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        entry_container.pack(pady=10)
        
        self.ingredient_entry = ctk.CTkEntry(
            entry_container,
            placeholder_text="Enter ingredient (e.g., chicken, tomatoes...)",
            width=400,
            height=40,
            font=("Helvetica", 16)
        )
        self.ingredient_entry.pack(side="left", padx=10)
        
        # Bind Enter key to add ingredient
        self.ingredient_entry.bind('<Return>', lambda e: self.add_ingredient_to_list(self.ingredient_entry.get()))
        
        add_btn = ctk.CTkButton(
            entry_container,
            text="+ Add",
            width=100,
            height=40,
            font=("Helvetica", 16, "bold"),
            fg_color=self.colors['primary'],
            command=lambda: self.add_ingredient_to_list(self.ingredient_entry.get())
        )
        add_btn.pack(side="left")
        
        # Current ingredients display
        self.ingredients_display_frame = ctk.CTkFrame(input_frame, fg_color=self.colors['bg_light'], corner_radius=10)
        self.ingredients_display_frame.pack(fill="x", padx=20, pady=20)
        
        self.update_ingredients_display()
        
        # Button row
        button_container = ctk.CTkFrame(input_frame, fg_color="transparent")
        button_container.pack(pady=20)
        
        # Find button
        find_btn = ctk.CTkButton(
            button_container,
            text="🔍 Find Matching Recipes",
            font=("Helvetica", 18, "bold"),
            width=250,
            height=50,
            corner_radius=10,
            fg_color=self.colors['secondary'],
            command=self.find_matching_recipes
        )
        find_btn.pack(side="left", padx=10)
        
        # Clear button
        clear_btn = ctk.CTkButton(
            button_container,
            text="�️ Clear All",
            font=("Helvetica", 18, "bold"),
            width=150,
            height=50,
            corner_radius=10,
            fg_color=self.colors['accent'],
            command=self.clear_ingredients
        )
        clear_btn.pack(side="left", padx=10)
        
        # Results area
        self.results_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        self.results_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Initial message
        if not self.available_ingredients:
            placeholder = ctk.CTkLabel(
                self.results_container,
                text="👆 Add ingredients above and click 'Find Matching Recipes'",
                font=("Helvetica", 16),
                text_color=self.colors['text_dark']
            )
            placeholder.pack(pady=50)
    
    def show_list_tab(self):
        """Display grocery list tab"""
        self.clear_content()
        self.update_status("Grocery List Generator")
        
        # Initialize selected recipes if not already done
        if not hasattr(self, 'selected_recipe_ids'):
            self.selected_recipe_ids = set()
        
        # Check if we're viewing a generated list
        if hasattr(self, 'viewing_grocery_list') and self.viewing_grocery_list:
            self.display_generated_grocery_list()
            return
        
        # Main container - use same packing as generated list view
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Title
        title = ctk.CTkLabel(
            main_container,
            text="📝 Grocery List Generator",
            font=("Helvetica", 24, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(pady=(5, 10))
        
        # Instructions
        instructions = ctk.CTkLabel(
            main_container,
            text="Select recipes below to generate a combined shopping list",
            font=("Helvetica", 14),
            text_color=self.colors['text_dark']
        )
        instructions.pack(pady=(0, 10))
        
        # Search and filter bar
        search_frame = ctk.CTkFrame(main_container, fg_color=self.colors['card_bg'], corner_radius=10)
        search_frame.pack(fill="x", pady=(0, 5))
        
        # Search entry
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(side="left", padx=20, pady=15)
        
        search_label = ctk.CTkLabel(
            search_container,
            text="�",
            font=("Helvetica", 18)
        )
        search_label.pack(side="left", padx=(0, 10))
        
        self.list_search_entry = ctk.CTkEntry(
            search_container,
            placeholder_text="Search recipes...",
            width=300,
            height=35,
            font=("Helvetica", 14)
        )
        self.list_search_entry.pack(side="left")
        self.list_search_entry.bind('<KeyRelease>', lambda e: self.refresh_recipe_selection_list())
        
        # Selection controls
        controls_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        controls_container.pack(side="right", padx=20, pady=15)
        
        select_all_btn = ctk.CTkButton(
            controls_container,
            text="✓ Select All",
            width=120,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors['secondary'],
            command=self.select_all_recipes
        )
        select_all_btn.pack(side="left", padx=5)
        
        clear_btn = ctk.CTkButton(
            controls_container,
            text="✗ Clear All",
            width=120,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors['accent'],
            command=self.clear_all_recipes
        )
        clear_btn.pack(side="left", padx=5)
        
        # Recipe selection area (scrollable) - Use both to expand but not push button off screen
        self.recipe_selection_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color=self.colors['card_bg'],
            corner_radius=15
        )
        self.recipe_selection_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        # Bottom section with count and button - Create BEFORE loading recipes
        bottom_section = ctk.CTkFrame(main_container, fg_color="transparent")
        bottom_section.pack(fill="x", pady=(5, 0))
        
        # Selected count display
        self.selected_count_label = ctk.CTkLabel(
            bottom_section,
            text=f"Selected: {len(self.selected_recipe_ids)} recipes",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['primary']
        )
        self.selected_count_label.pack(pady=(5, 10))
        
        # Generate button - Centered and prominent
        generate_btn = ctk.CTkButton(
            bottom_section,
            text="✨ Generate Grocery List",
            font=("Helvetica", 18, "bold"),
            width=280,
            height=55,
            corner_radius=12,
            fg_color=self.colors['primary'],
            hover_color="#27AE60",
            command=self.generate_grocery_list
        )
        generate_btn.pack(pady=(0, 10))
        
        # Load recipes AFTER creating the label so it can be updated
        self.refresh_recipe_selection_list()
    
    # ========== FUNCTIONALITY METHODS ==========
    
    def start_scan_dialog(self):
        """Start scanner using Windows dialog (easiest for users)"""
        if not self.scanner.is_available():
            messagebox.showerror("Scanner Error", "Scanner functionality not available.\n\nPlease ensure:\n1. pywin32 is installed\n2. Scanner is connected and powered on\n3. Scanner drivers are installed")
            return
        
        self.update_status("Opening scanner dialog...")
        
        # Show Windows scan dialog
        try:
            # scan_with_dialog now returns a list of image paths
            scanned_images = self.scanner.scan_with_dialog()
            
            if scanned_images:
                # Handle single or multiple pages
                num_pages = len(scanned_images)
                
                if num_pages == 1:
                    # Single page scan
                    self.current_scanned_image = scanned_images[0]
                    self.scanned_pages = []  # Clear any previous pages
                    self.update_status(f"Scan complete: {Path(scanned_images[0]).name}")
                    
                    # Show preview
                    self.display_scanned_preview(scanned_images[0])
                    
                    # Ask if user wants to process with OCR
                    result = messagebox.askyesno(
                        "Scan Complete",
                        "Recipe scanned successfully!\n\nWould you like to process it with OCR now?"
                    )
                    if result:
                        self.process_scanned_image()
                else:
                    # Multiple pages scanned
                    self.scanned_pages = scanned_images[:-1]  # All but last
                    self.current_scanned_image = scanned_images[-1]  # Last page
                    self.update_status(f"Scan complete: {num_pages} pages scanned")
                    
                    # Show preview of last page
                    self.display_scanned_preview(scanned_images[-1])
                    
                    # Ask if user wants to process all pages with OCR
                    result = messagebox.askyesno(
                        "Multi-Page Scan Complete",
                        f"{num_pages} pages scanned successfully from document feeder!\n\n"
                        f"Pages scanned: {num_pages}\n\n"
                        f"Would you like to process all pages with OCR now?"
                    )
                    if result:
                        self.process_scanned_image()
            else:
                self.update_status("Scan cancelled")
                
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning image:\n{str(e)}")
            self.update_status("Scan failed")
    
    def scan_next_page(self):
        """Scan an additional page for a multi-page recipe"""
        if not self.scanner.is_available():
            messagebox.showerror("Scanner Error", "Scanner not available!")
            return
        
        self.update_status("Scanning next page...")
        
        try:
            # Save current page to scanned_pages list
            if self.current_scanned_image and self.current_scanned_image not in self.scanned_pages:
                self.scanned_pages.append(self.current_scanned_image)
            
            # Scan new page(s) - may return multiple if using feeder
            scanned_images = self.scanner.scan_with_dialog()
            
            if scanned_images:
                num_new_pages = len(scanned_images)
                
                if num_new_pages == 1:
                    # Single page
                    self.current_scanned_image = scanned_images[0]
                    page_num = len(self.scanned_pages) + 1
                    self.update_status(f"Page {page_num} scanned")
                    
                    # Show preview
                    self.display_scanned_preview(scanned_images[0])
                    
                    messagebox.showinfo(
                        "Page Scanned",
                        f"Page {page_num} scanned successfully!\n\nYou can:\n• Scan more pages (click 'Scan Next Page')\n• Process all pages with OCR (click 'Process with OCR')"
                    )
                else:
                    # Multiple pages from feeder
                    self.scanned_pages.extend(scanned_images[:-1])
                    self.current_scanned_image = scanned_images[-1]
                    total_pages = len(self.scanned_pages) + 1
                    self.update_status(f"{num_new_pages} pages scanned (total: {total_pages})")
                    
                    # Show preview of last page
                    self.display_scanned_preview(scanned_images[-1])
                    
                    messagebox.showinfo(
                        "Pages Scanned",
                        f"{num_new_pages} additional pages scanned from feeder!\n\n"
                        f"Total pages: {total_pages}\n\n"
                        f"You can:\n• Scan more pages (click 'Scan Next Page')\n• Process all pages with OCR (click 'Process with OCR')"
                    )
            else:
                self.update_status("Scan cancelled")
                
        except Exception as e:
            messagebox.showerror("Scan Error", f"Error scanning page:\n{str(e)}")
            self.update_status("Scan failed")
    
    def import_image(self):
        """Import an existing image or PDF file"""
        file_path = filedialog.askopenfilename(
            title="Select Recipe Image or PDF",
            filetypes=[
                ("Recipe files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.pdf"),
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("PDF files", "*.pdf"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            # Check if it's a PDF
            is_pdf = file_path.lower().endswith('.pdf')
            
            if is_pdf:
                self.update_status("Converting PDF to images...")
            else:
                self.update_status("Importing image...")
            
            try:
                # Import file (handles both images and PDFs)
                imported_paths = self.scanner.scan_from_file(file_path)
                
                if imported_paths:
                    num_pages = len(imported_paths)
                    
                    if num_pages == 1:
                        # Single page/image
                        self.current_scanned_image = imported_paths[0]
                        self.scanned_pages = []
                        self.update_status(f"Imported: {Path(file_path).name}")
                        
                        # Show preview
                        self.display_scanned_preview(imported_paths[0])
                        
                        # Ask if user wants to process with OCR
                        result = messagebox.askyesno(
                            "Import Complete",
                            f"{'PDF converted' if is_pdf else 'Image imported'} successfully!\n\nWould you like to process it with OCR now?"
                        )
                        if result:
                            self.process_scanned_image()
                    
                    else:
                        # Multi-page PDF
                        self.scanned_pages = imported_paths[:-1]
                        self.current_scanned_image = imported_paths[-1]
                        self.update_status(f"Imported {num_pages} pages from PDF")
                        
                        # Show preview of last page
                        self.display_scanned_preview(imported_paths[-1])
                        
                        # Ask if user wants to process with OCR
                        result = messagebox.askyesno(
                            "Import Complete",
                            f"PDF converted to {num_pages} pages!\n\nWould you like to process all pages with OCR now?"
                        )
                        if result:
                            self.process_scanned_image()
                else:
                    messagebox.showerror("Import Error", "Failed to import file")
                    self.update_status("Import failed")
                    
            except Exception as e:
                messagebox.showerror("Import Error", f"Error importing file:\n{str(e)}")
                self.update_status("Import failed")
    
    def display_scanned_preview(self, image_path):
        """Display preview of scanned image"""
        try:
            # Load and resize image
            img = Image.open(image_path)
            
            # Calculate size to fit in preview frame (700x500)
            img.thumbnail((680, 480), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage for CTk
            photo = ImageTk.PhotoImage(img)
            
            # Update preview label
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # Keep reference
            
            # Refresh the scan tab to show process button
            self.show_scan_tab()
            
        except Exception as e:
            print(f"Error displaying preview: {e}")
            messagebox.showerror("Preview Error", f"Could not display image preview:\n{str(e)}")
    
    def process_scanned_image(self):
        """Process scanned image with OCR"""
        if not self.current_scanned_image:
            messagebox.showwarning("No Image", "Please scan or import an image first!")
            return
        
        # Check if OCR is available
        if not self.ocr.is_available():
            messagebox.showerror(
                "OCR Not Available",
                "Tesseract OCR is not installed or not configured.\n\n"
                "Please install Tesseract:\n"
                "1. Download from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install it\n"
                "3. Restart the application"
            )
            return
        
        self.update_status("Extracting text with OCR...")
        
        try:
            # Collect all pages to process
            pages_to_process = []
            if self.scanned_pages:
                pages_to_process = self.scanned_pages.copy()
            if self.current_scanned_image:
                if self.current_scanned_image not in pages_to_process:
                    pages_to_process.append(self.current_scanned_image)
            
            if not pages_to_process:
                messagebox.showwarning("No Image", "No scanned pages found!")
                return
            
            # Extract text from all pages
            all_text = []
            total_confidence = 0
            
            for i, page_path in enumerate(pages_to_process, 1):
                self.update_status(f"Extracting text from page {i}/{len(pages_to_process)}...")
                
                extracted_data = self.ocr.extract_text_with_confidence(
                    page_path,
                    preprocess=True
                )
                
                if extracted_data['text']:
                    all_text.append(extracted_data['text'])
                    total_confidence += extracted_data['confidence']
            
            if not all_text:
                messagebox.showwarning(
                    "No Text Found",
                    "Could not extract any text from the image(s).\n\n"
                    "Tips:\n"
                    "- Ensure the image is clear and well-lit\n"
                    "- Text should be horizontal\n"
                    "- Try rescanning with higher resolution"
                )
                self.update_status("OCR failed - no text extracted")
                return
            
            # Combine text from all pages
            raw_text = "\n\n=== PAGE BREAK ===\n\n".join(all_text)
            average_confidence = total_confidence / len(pages_to_process)
            
            page_info = f" from {len(pages_to_process)} pages" if len(pages_to_process) > 1 else ""
            self.update_status(f"Text extracted{page_info} (confidence: {average_confidence:.1f}%) - Parsing recipe...")
            
            # Parse the extracted text into recipe structure
            recipe_data = self.ocr.extract_structured_data(raw_text)
            recipe_data['raw_text'] = raw_text  # Store for "View Raw Text" button
            
            # Show the OCR results in an editable form
            self.show_ocr_results(recipe_data, average_confidence)
            
        except Exception as e:
            messagebox.showerror("OCR Error", f"Error processing image:\n{str(e)}")
            self.update_status("OCR processing failed")
    
    def show_ocr_results(self, recipe_data: dict, confidence: float):
        """Show OCR results in an editable form"""
        self.clear_content()
        self.update_status("Review OCR Results")
        
        # Create scrollable form
        form_container = ctk.CTkScrollableFrame(self.content_frame, fg_color=self.colors['bg_light'])
        form_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            form_container,
            text="✅ OCR Complete - Review & Save",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(pady=20)
        
        # Confidence indicator
        conf_color = self.colors['success'] if confidence > 80 else self.colors['warning'] if confidence > 60 else self.colors['accent']
        conf_label = ctk.CTkLabel(
            form_container,
            text=f"📊 OCR Confidence: {confidence:.1f}%",
            font=("Helvetica", 14),
            text_color=conf_color
        )
        conf_label.pack(pady=5)
        
        info_label = ctk.CTkLabel(
            form_container,
            text="Please review and edit the extracted information below, then click Save",
            font=("Helvetica", 14),
            text_color=self.colors['text_dark']
        )
        info_label.pack(pady=10)
        
        # Form frame
        form_frame = ctk.CTkFrame(form_container, fg_color=self.colors['card_bg'], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Recipe Name
        name_label = ctk.CTkLabel(form_frame, text="Recipe Name:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        name_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        name_entry = ctk.CTkEntry(form_frame, width=600, height=40, font=("Helvetica", 14))
        name_entry.insert(0, recipe_data.get('title', 'Untitled Recipe'))
        name_entry.pack(pady=(0, 15), padx=20)
        
        # Category
        category_label = ctk.CTkLabel(form_frame, text="Category:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        category_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        category_dropdown = ctk.CTkOptionMenu(form_frame, values=self.category_options, width=300, height=40, font=("Helvetica", 14))
        category_dropdown.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Servings and Time
        details_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Servings
        servings_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        servings_container.pack(side="left", padx=(0, 20))
        
        servings_label = ctk.CTkLabel(servings_container, text="Servings:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        servings_label.pack(anchor="w", pady=(0, 5))
        
        servings_entry = ctk.CTkEntry(servings_container, width=150, height=40, font=("Helvetica", 14))
        servings_entry.insert(0, recipe_data.get('servings', ''))
        servings_entry.pack()
        
        # Prep Time
        prep_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        prep_container.pack(side="left", padx=(0, 20))
        
        prep_label = ctk.CTkLabel(prep_container, text="Prep Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        prep_label.pack(anchor="w", pady=(0, 5))
        
        prep_entry = ctk.CTkEntry(prep_container, width=150, height=40, font=("Helvetica", 14))
        prep_entry.insert(0, recipe_data.get('prep_time', ''))
        prep_entry.pack()
        
        # Cook Time
        cook_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        cook_container.pack(side="left")
        
        cook_label = ctk.CTkLabel(cook_container, text="Cook Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        cook_label.pack(anchor="w", pady=(0, 5))
        
        cook_entry = ctk.CTkEntry(cook_container, width=150, height=40, font=("Helvetica", 14))
        cook_entry.insert(0, recipe_data.get('cook_time', ''))
        cook_entry.pack()
        
        # Ingredients
        ingredients_label = ctk.CTkLabel(form_frame, text="Ingredients (one per line):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        ingredients_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        ingredients_text = ctk.CTkTextbox(form_frame, width=600, height=200, font=("Helvetica", 14))
        ingredients_content = '\n'.join(recipe_data.get('ingredients', [])) if recipe_data.get('ingredients') else ''
        ingredients_text.insert("1.0", ingredients_content)
        ingredients_text.pack(pady=(0, 15), padx=20)
        
        # Instructions
        instructions_label = ctk.CTkLabel(form_frame, text="Instructions:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        instructions_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        instructions_text = ctk.CTkTextbox(form_frame, width=600, height=300, font=("Helvetica", 14))
        instructions_content = '\n\n'.join([f"{i+1}. {inst}" for i, inst in enumerate(recipe_data.get('instructions', []))]) if recipe_data.get('instructions') else ''
        instructions_text.insert("1.0", instructions_content)
        instructions_text.pack(pady=(0, 15), padx=20)
        
        # Variations
        variations_label = ctk.CTkLabel(form_frame, text="Variations:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        variations_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        variations_text = ctk.CTkTextbox(form_frame, width=600, height=100, font=("Helvetica", 14))
        variations_content = recipe_data.get('variations', '')
        variations_text.insert("1.0", variations_content)
        variations_text.pack(pady=(0, 15), padx=20)
        
        # Notes
        notes_label = ctk.CTkLabel(form_frame, text="Notes:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        notes_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        notes_text = ctk.CTkTextbox(form_frame, width=600, height=100, font=("Helvetica", 14))
        notes_content = recipe_data.get('notes', '')
        notes_text.insert("1.0", notes_content)
        notes_text.pack(pady=(0, 15), padx=20)
        
        # Tags
        tags_label = ctk.CTkLabel(form_frame, text="Tags (comma-separated):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        tags_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        tags_entry = ctk.CTkEntry(form_frame, width=600, height=40, font=("Helvetica", 14))
        tags_entry.insert(0, "scanned")  # Default tag
        tags_entry.pack(pady=(0, 20), padx=20)
        
        # Image options section
        image_section = ctk.CTkFrame(form_frame, fg_color=self.colors['bg_light'], corner_radius=10)
        image_section.pack(fill="x", padx=20, pady=(10, 20))
        
        image_title = ctk.CTkLabel(
            image_section,
            text="Recipe Image:",
            font=("Helvetica", 16, "bold"),
            text_color=self.colors['text_dark']
        )
        image_title.pack(pady=(10, 5), padx=15, anchor="w")
        
        # Store the cropped image path
        self.cropped_image_path = None
        
        # Button frame for image options
        image_btn_frame = ctk.CTkFrame(image_section, fg_color="transparent")
        image_btn_frame.pack(pady=(5, 10), padx=15, anchor="w")
        
        # Crop image button
        crop_btn = ctk.CTkButton(
            image_btn_frame,
            text="✂️ Crop & Add Image",
            font=("Helvetica", 14, "bold"),
            width=180,
            height=40,
            fg_color=self.colors['primary'],
            command=lambda: self.crop_scanned_image()
        )
        crop_btn.pack(side="left", padx=5)
        
        # Status label
        self.image_status_label = ctk.CTkLabel(
            image_btn_frame,
            text="No image selected",
            font=("Helvetica", 12),
            text_color=self.colors['text_dark']
        )
        self.image_status_label.pack(side="left", padx=10)
        
        image_info = ctk.CTkLabel(
            image_section,
            text="💡 Tip: Use 'Crop & Add Image' to select and crop the recipe portion from the scanned page",
            font=("Helvetica", 11, "italic"),
            text_color=self.colors['text_dark'],
            wraplength=550,
            justify="left"
        )
        image_info.pack(pady=(0, 10), padx=15, anchor="w")
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Recipe",
            font=("Helvetica", 18, "bold"),
            width=200,
            height=50,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=lambda: self.save_ocr_recipe(
                name_entry.get(),
                category_dropdown.get(),
                servings_entry.get(),
                prep_entry.get(),
                cook_entry.get(),
                ingredients_text.get("1.0", "end-1c"),
                instructions_text.get("1.0", "end-1c"),
                variations_text.get("1.0", "end-1c"),
                notes_text.get("1.0", "end-1c"),
                tags_entry.get()
            )
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            font=("Helvetica", 18, "bold"),
            width=150,
            height=50,
            corner_radius=10,
            fg_color=self.colors['accent'],
            command=self.show_scan_tab
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Show raw text button
        raw_btn = ctk.CTkButton(
            button_frame,
            text="📄 View Raw OCR Text",
            font=("Helvetica", 18, "bold"),
            width=220,
            height=50,
            corner_radius=10,
            fg_color=self.colors['secondary'],
            command=lambda: self.show_raw_ocr_text(recipe_data.get('raw_text', 'No raw text available'))
        )
        raw_btn.pack(side="left", padx=10)
    
    def show_raw_ocr_text(self, raw_text):
        """Show raw OCR text in a copyable dialog"""
        # Create a new top-level window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Raw OCR Text")
        dialog.geometry("800x600")
        dialog.transient(self)
        # Don't use grab_set() so user can interact with both windows
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text="📄 Raw OCR Text (Select and Copy)",
            font=("Helvetica", 20, "bold"),
            text_color=self.colors['secondary']
        )
        title.pack(pady=15)
        
        # Info label
        info = ctk.CTkLabel(
            dialog,
            text="You can select and copy text from below (Ctrl+C to copy)",
            font=("Helvetica", 12),
            text_color=self.colors['text_dark']
        )
        info.pack(pady=(0, 10))
        
        # Text frame
        text_frame = ctk.CTkFrame(dialog)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Textbox with raw text - editable for selection/copy
        text_box = ctk.CTkTextbox(
            text_frame,
            font=("Arial", 14),
            wrap="word"
        )
        text_box.pack(fill="both", expand=True, padx=5, pady=5)
        text_box.insert("1.0", raw_text)
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            font=("Helvetica", 14, "bold"),
            width=150,
            height=40,
            fg_color=self.colors['accent'],
            command=dialog.destroy
        )
        close_btn.pack(pady=(0, 15))
    
    def crop_scanned_image(self):
        """Open a dialog to crop the scanned image"""
        if not self.current_scanned_image or not os.path.exists(self.current_scanned_image):
            messagebox.showwarning("No Image", "No scanned image available to crop!")
            return
        
        # Build list of available pages
        available_pages = []
        if self.scanned_pages:
            # Add all scanned pages
            for page in self.scanned_pages:
                if os.path.exists(page):
                    available_pages.append(page)
        # Always add current page if not already in list
        if self.current_scanned_image not in available_pages and os.path.exists(self.current_scanned_image):
            available_pages.append(self.current_scanned_image)
        
        if not available_pages:
            messagebox.showwarning("No Image", "No scanned images available to crop!")
            return
        
        # If multiple pages, let user choose which one to crop
        selected_image = None
        if len(available_pages) > 1:
            # Create page selection dialog
            page_dialog = ctk.CTkToplevel(self)
            page_dialog.title("Select Page to Crop")
            page_dialog.geometry("400x300")
            page_dialog.transient(self)
            page_dialog.grab_set()
            
            title = ctk.CTkLabel(
                page_dialog,
                text="Select Page to Crop",
                font=("Helvetica", 16, "bold"),
                text_color=self.colors['secondary']
            )
            title.pack(pady=20)
            
            info = ctk.CTkLabel(
                page_dialog,
                text="Multiple pages detected.\nWhich page has the recipe image?",
                font=("Helvetica", 12),
                text_color=self.colors['text_dark']
            )
            info.pack(pady=(0, 20))
            
            selected_page_var = ctk.StringVar(value="Page 1")
            
            # Create radio buttons for each page
            for idx, page_path in enumerate(available_pages, 1):
                page_name = f"Page {idx}"
                radio = ctk.CTkRadioButton(
                    page_dialog,
                    text=page_name,
                    variable=selected_page_var,
                    value=page_name,
                    font=("Helvetica", 13),
                    text_color=self.colors['text_dark']
                )
                radio.pack(pady=5)
            
            def confirm_selection():
                selected = selected_page_var.get()
                page_num = int(selected.split()[1]) - 1
                nonlocal selected_image
                selected_image = available_pages[page_num]
                page_dialog.destroy()
            
            button_frame = ctk.CTkFrame(page_dialog, fg_color="transparent")
            button_frame.pack(pady=20)
            
            ok_btn = ctk.CTkButton(
                button_frame,
                text="OK",
                width=100,
                height=35,
                font=("Helvetica", 12, "bold"),
                fg_color=self.colors['success'],
                command=confirm_selection
            )
            ok_btn.pack(side="left", padx=10)
            
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="Cancel",
                width=100,
                height=35,
                font=("Helvetica", 12, "bold"),
                fg_color=self.colors['accent'],
                command=page_dialog.destroy
            )
            cancel_btn.pack(side="left", padx=10)
            
            # Wait for dialog to close
            self.wait_window(page_dialog)
            
            if not selected_image:
                return  # User cancelled
        else:
            # Single page, use it directly
            selected_image = available_pages[0]
        
        try:
            # Open the selected image
            original_image = Image.open(selected_image)
            
            # Create crop dialog
            crop_dialog = ctk.CTkToplevel(self)
            crop_dialog.title("Crop Recipe Image")
            crop_dialog.geometry("1000x800")
            crop_dialog.transient(self)
            crop_dialog.grab_set()
            
            # Title
            title = ctk.CTkLabel(
                crop_dialog,
                text="✂️ Crop Recipe Image",
                font=("Helvetica", 20, "bold"),
                text_color=self.colors['secondary']
            )
            title.pack(pady=15)
            
            # Instructions
            instructions = ctk.CTkLabel(
                crop_dialog,
                text="Click and drag to select the area you want to keep. Click 'Save Crop' when done.",
                font=("Helvetica", 12),
                text_color=self.colors['text_dark']
            )
            instructions.pack(pady=(0, 10))
            
            # Canvas frame
            canvas_frame = ctk.CTkFrame(crop_dialog)
            canvas_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
            
            # Create canvas for image display
            import tkinter as tk
            canvas = tk.Canvas(canvas_frame, bg='gray', cursor="cross")
            canvas.pack(fill="both", expand=True)
            
            # Scale image to fit canvas
            max_width = 960
            max_height = 600
            img_width, img_height = original_image.size
            scale = min(max_width / img_width, max_height / img_height, 1.0)
            
            display_width = int(img_width * scale)
            display_height = int(img_height * scale)
            
            display_image = original_image.copy()
            display_image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            
            # Display image on canvas
            canvas.create_image(0, 0, anchor='nw', image=photo)
            canvas.image = photo  # Keep a reference
            canvas.config(width=display_width, height=display_height)
            
            # Variables for crop rectangle
            crop_rect = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0, 'id': None}
            
            def on_mouse_down(event):
                crop_rect['x1'] = event.x
                crop_rect['y1'] = event.y
                if crop_rect['id']:
                    canvas.delete(crop_rect['id'])
            
            def on_mouse_drag(event):
                crop_rect['x2'] = event.x
                crop_rect['y2'] = event.y
                if crop_rect['id']:
                    canvas.delete(crop_rect['id'])
                crop_rect['id'] = canvas.create_rectangle(
                    crop_rect['x1'], crop_rect['y1'],
                    crop_rect['x2'], crop_rect['y2'],
                    outline='red', width=3
                )
            
            def on_mouse_up(event):
                crop_rect['x2'] = event.x
                crop_rect['y2'] = event.y
            
            # Bind mouse events
            canvas.bind('<ButtonPress-1>', on_mouse_down)
            canvas.bind('<B1-Motion>', on_mouse_drag)
            canvas.bind('<ButtonRelease-1>', on_mouse_up)
            
            def save_cropped_image():
                """Save the cropped region"""
                x1, y1 = crop_rect['x1'], crop_rect['y1']
                x2, y2 = crop_rect['x2'], crop_rect['y2']
                
                # Ensure coordinates are in correct order
                left = min(x1, x2)
                top = min(y1, y2)
                right = max(x1, x2)
                bottom = max(y1, y2)
                
                # Check if selection is valid
                if right - left < 10 or bottom - top < 10:
                    messagebox.showwarning("Invalid Selection", "Please select a larger area!")
                    return
                
                # Convert display coordinates to original image coordinates
                orig_left = int(left / scale)
                orig_top = int(top / scale)
                orig_right = int(right / scale)
                orig_bottom = int(bottom / scale)
                
                # Crop the original image
                cropped = original_image.crop((orig_left, orig_top, orig_right, orig_bottom))
                
                # Save cropped image
                crop_dir = Path("scanned_images/cropped")
                crop_dir.mkdir(parents=True, exist_ok=True)
                
                timestamp = Path(selected_image).stem
                crop_path = crop_dir / f"{timestamp}_cropped.png"
                cropped.save(crop_path, "PNG")
                
                self.cropped_image_path = str(crop_path)
                
                # Update status label
                if hasattr(self, 'image_status_label'):
                    self.image_status_label.configure(text="✓ Image cropped and ready")
                
                messagebox.showinfo("Success", "Image cropped successfully!")
                crop_dialog.destroy()
            
            # Button frame
            button_frame = ctk.CTkFrame(crop_dialog)
            button_frame.pack(pady=15)
            
            save_btn = ctk.CTkButton(
                button_frame,
                text="💾 Save Crop",
                font=("Helvetica", 14, "bold"),
                width=150,
                height=40,
                fg_color=self.colors['success'],
                command=save_cropped_image
            )
            save_btn.pack(side="left", padx=10)
            
            cancel_btn = ctk.CTkButton(
                button_frame,
                text="❌ Cancel",
                font=("Helvetica", 14, "bold"),
                width=150,
                height=40,
                fg_color=self.colors['accent'],
                command=crop_dialog.destroy
            )
            cancel_btn.pack(side="left", padx=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image for cropping:\n{str(e)}")
    
    def save_ocr_recipe(self, name, category, servings, prep_time, cook_time, ingredients, instructions, variations, notes, tags):
        """Save OCR-extracted recipe"""
        if not name:
            messagebox.showwarning("Missing Info", "Please enter a recipe name!")
            return
        
        if not ingredients.strip():
            messagebox.showwarning("Missing Info", "Please enter ingredients!")
            return
        
        if not instructions.strip():
            messagebox.showwarning("Missing Info", "Please enter instructions!")
            return
        
        try:
            # Parse ingredients and instructions
            ingredient_list = [line.strip() for line in ingredients.split('\n') if line.strip()]
            instruction_list = [line.strip() for line in instructions.split('\n') if line.strip()]
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Use cropped image if available
            image_path_to_save = None
            if hasattr(self, 'cropped_image_path') and self.cropped_image_path:
                image_path_to_save = self.cropped_image_path
            
            # Save to database
            recipe_id = self.db.add_recipe(
                name=name,
                category=category,
                servings=servings,
                prep_time=prep_time,
                cook_time=cook_time,
                ingredients=ingredient_list,
                instructions=instruction_list,
                tags=tag_list,
                source='scanned',
                image_path=image_path_to_save,
                variations=variations.strip(),
                notes=notes.strip()
            )
            
            messagebox.showinfo("Success", f"Recipe '{name}' saved successfully!\n\nRecipe ID: {recipe_id}\n\nYou can now find it in the Browse tab.")
            self.update_status(f"Saved scanned recipe: {name}")
            self.update_recipe_count()
            
            # Clear scanned images
            self.current_scanned_image = None
            self.scanned_pages = []
            self.combined_ocr_text = ""
            
            # Go to browse tab to see the new recipe
            self.show_browse_tab()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recipe:\n{str(e)}")
            self.update_status("Error saving recipe")
    
    def add_ingredient_to_list(self, ingredient):
        """Add ingredient to matcher list"""
        if not ingredient or not ingredient.strip():
            return
        
        ingredient = ingredient.strip()
        
        # Check if already in list
        if ingredient.lower() not in [ing.lower() for ing in self.available_ingredients]:
            self.available_ingredients.append(ingredient)
            self.update_status(f"Added: {ingredient}")
            
            # Clear entry and refresh display
            self.ingredient_entry.delete(0, 'end')
            self.update_ingredients_display()
        else:
            messagebox.showinfo("Already Added", f"'{ingredient}' is already in your list!")
    
    def remove_ingredient_from_list(self, ingredient):
        """Remove ingredient from list"""
        if ingredient in self.available_ingredients:
            self.available_ingredients.remove(ingredient)
            self.update_status(f"Removed: {ingredient}")
            self.update_ingredients_display()
    
    def clear_ingredients(self):
        """Clear all ingredients"""
        if self.available_ingredients:
            result = messagebox.askyesno("Clear All", "Remove all ingredients from the list?")
            if result:
                self.available_ingredients.clear()
                self.update_status("Ingredients cleared")
                self.show_match_tab()
        else:
            messagebox.showinfo("Empty", "No ingredients to clear!")
    
    def update_ingredients_display(self):
        """Update the ingredients display area"""
        # Clear current display
        for widget in self.ingredients_display_frame.winfo_children():
            widget.destroy()
        
        if not self.available_ingredients:
            placeholder = ctk.CTkLabel(
                self.ingredients_display_frame,
                text="No ingredients added yet",
                font=("Helvetica", 14),
                text_color=self.colors['text_dark']
            )
            placeholder.pack(pady=20)
        else:
            # Title
            count_label = ctk.CTkLabel(
                self.ingredients_display_frame,
                text=f"Your Ingredients ({len(self.available_ingredients)}):",
                font=("Helvetica", 16, "bold"),
                text_color=self.colors['primary']
            )
            count_label.pack(pady=10)
            
            # Ingredient tags
            tags_container = ctk.CTkFrame(self.ingredients_display_frame, fg_color="transparent")
            tags_container.pack(fill="x", padx=10, pady=10)
            
            for ingredient in self.available_ingredients:
                tag_frame = ctk.CTkFrame(tags_container, fg_color=self.colors['primary'], corner_radius=20)
                tag_frame.pack(side="left", padx=5, pady=5)
                
                tag_label = ctk.CTkLabel(
                    tag_frame,
                    text=ingredient,
                    font=("Helvetica", 14),
                    text_color="white"
                )
                tag_label.pack(side="left", padx=(15, 5), pady=5)
                
                remove_btn = ctk.CTkButton(
                    tag_frame,
                    text="✕",
                    width=25,
                    height=25,
                    font=("Helvetica", 14, "bold"),
                    fg_color="transparent",
                    hover_color=self.colors['accent'],
                    command=lambda ing=ingredient: self.remove_ingredient_from_list(ing)
                )
                remove_btn.pack(side="left", padx=(0, 10), pady=5)
    
    def find_matching_recipes(self):
        """Find recipes matching ingredients"""
        if not self.available_ingredients:
            messagebox.showwarning("No Ingredients", "Please add some ingredients first!")
            return
        
        self.update_status("Searching for matching recipes...")
        
        try:
            # Find matches
            matches = self.matcher.find_matching_recipes(
                self.available_ingredients,
                match_threshold=0.1  # Show recipes with at least 10% match (1+ ingredients)
            )
            
            # Clear results container
            for widget in self.results_container.winfo_children():
                widget.destroy()
            
            if not matches:
                no_results = ctk.CTkLabel(
                    self.results_container,
                    text="😕 No matching recipes found\n\nTry adding more ingredients or check your recipe collection",
                    font=("Helvetica", 16),
                    text_color=self.colors['text_dark'],
                    justify="center"
                )
                no_results.pack(pady=50)
                self.update_status("No matches found")
                return
            
            # Display results
            results_title = ctk.CTkLabel(
                self.results_container,
                text=f"🎯 Found {len(matches)} Matching Recipes",
                font=("Helvetica", 22, "bold"),
                text_color=self.colors['success']
            )
            results_title.pack(pady=20)
            
            # Categorize results
            perfect_matches = [r for r in matches if r['match_percentage'] >= 1.0]
            close_matches = [r for r in matches if 0.7 <= r['match_percentage'] < 1.0]
            partial_matches = [r for r in matches if r['match_percentage'] < 0.7]
            
            # Perfect matches
            if perfect_matches:
                self._display_match_category(
                    self.results_container,
                    "✅ Can Make Now (100% Match)",
                    perfect_matches,
                    self.colors['success']
                )
            
            # Close matches
            if close_matches:
                self._display_match_category(
                    self.results_container,
                    "📍 Almost There (70%+ Match)",
                    close_matches,
                    self.colors['warning']
                )
            
            # Partial matches
            if partial_matches:
                self._display_match_category(
                    self.results_container,
                    "🔍 Partial Matches (30%+ Match)",
                    partial_matches,
                    self.colors['secondary']
                )
            
            self.update_status(f"Found {len(matches)} matching recipes")
            
        except Exception as e:
            messagebox.showerror("Search Error", f"Error searching recipes:\n{str(e)}")
            self.update_status("Search failed")
    
    def _display_match_category(self, parent, title, recipes, color):
        """Display a category of matching recipes"""
        # Category title
        category_label = ctk.CTkLabel(
            parent,
            text=title,
            font=("Helvetica", 18, "bold"),
            text_color=color
        )
        category_label.pack(pady=(20, 10), anchor="w")
        
        # Recipe cards
        for recipe in recipes:
            self._create_match_card(parent, recipe)
    
    def _create_match_card(self, parent, recipe):
        """Create a recipe match card"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['card_bg'], corner_radius=10)
        card.pack(fill="x", pady=5)
        
        # Main info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=10)
        
        # Recipe name
        name_label = ctk.CTkLabel(
            info_frame,
            text=recipe['name'],
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['primary'],
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Match percentage
        match_pct = recipe['match_percentage'] * 100
        match_color = self.colors['success'] if match_pct >= 100 else self.colors['warning'] if match_pct >= 70 else self.colors['secondary']
        
        match_label = ctk.CTkLabel(
            info_frame,
            text=f"{match_pct:.0f}% Match",
            font=("Helvetica", 16, "bold"),
            text_color=match_color,
            fg_color=self.colors['bg_light'],
            corner_radius=5,
            padx=15,
            pady=5
        )
        match_label.pack(side="right")
        
        # Ingredient info
        details_text = f"Have: {recipe['matching_ingredients']}/{recipe['total_ingredients']} ingredients"
        if recipe['missing_ingredients']:
            details_text += f" • Missing: {len(recipe['missing_ingredients'])}"
        
        details_label = ctk.CTkLabel(
            card,
            text=details_text,
            font=("Helvetica", 14),
            text_color=self.colors['text_dark'],
            anchor="w"
        )
        details_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Missing ingredients (if any)
        if recipe['missing_ingredients'] and len(recipe['missing_ingredients']) <= 5:
            missing_text = "Need: " + ", ".join(recipe['missing_ingredients'][:5])
            if len(recipe['missing_ingredients']) > 5:
                missing_text += f" (+{len(recipe['missing_ingredients']) - 5} more)"
            
            missing_label = ctk.CTkLabel(
                card,
                text=missing_text,
                font=("Helvetica", 12),
                text_color=self.colors['accent'],
                anchor="w"
            )
            missing_label.pack(fill="x", padx=15, pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        view_btn = ctk.CTkButton(
            button_frame,
            text="👁️ View Recipe",
            width=120,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors['primary'],
            command=lambda: self.view_recipe(recipe['id'])
        )
        view_btn.pack(side="left", padx=2)
        
        details_btn = ctk.CTkButton(
            button_frame,
            text="📋 Match Details",
            width=140,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors['secondary'],
            command=lambda: self.show_match_details(recipe['id'])
        )
        details_btn.pack(side="left", padx=2)
        
        print_btn = ctk.CTkButton(
            button_frame,
            text="🖨️ Print",
            width=100,
            height=35,
            font=("Helvetica", 14),
            fg_color=self.colors['warning'],
            command=lambda: self.print_recipe(recipe['id'])
        )
        print_btn.pack(side="left", padx=2)
    
    def show_match_details(self, recipe_id):
        """Show detailed match information for a recipe"""
        details = self.matcher.get_recipe_match_details(recipe_id, self.available_ingredients)
        
        if not details:
            messagebox.showerror("Error", "Could not load recipe details")
            return
        
        # Format message
        msg = f"Recipe: {details['recipe_name']}\n\n"
        msg += f"Match: {details['match_percentage']:.0f}%\n"
        msg += f"Have: {details['have_count']}/{details['total_count']} ingredients\n\n"
        
        if details['can_make']:
            msg += "✅ You can make this recipe!\n\n"
        else:
            msg += f"❌ Missing {details['need_count']} ingredient(s):\n"
            for ing in details['need']:
                msg += f"  • {ing}\n"
        
        messagebox.showinfo("Match Details", msg)
    
    def refresh_recipe_selection_list(self):
        """Refresh the recipe selection list with checkboxes"""
        # Clear existing widgets
        for widget in self.recipe_selection_frame.winfo_children():
            widget.destroy()
        
        # Get search term
        search_term = ""
        if hasattr(self, 'list_search_entry'):
            search_term = self.list_search_entry.get().strip().lower()
        
        # Get all recipes
        all_recipes = self.db.get_all_recipes()
        
        # Filter by search term
        if search_term:
            filtered_recipes = [
                r for r in all_recipes 
                if search_term in r['name'].lower() or 
                (r['category'] and search_term in r['category'].lower())
            ]
        else:
            filtered_recipes = all_recipes
        
        if not filtered_recipes:
            # No recipes found
            no_recipes = ctk.CTkLabel(
                self.recipe_selection_frame,
                text="📭\n\nNo recipes found!\n\nTry adjusting your search or add recipes first.",
                font=("Helvetica", 18),
                text_color=self.colors['text_dark']
            )
            no_recipes.pack(pady=100)
        else:
            # Display recipes with checkboxes
            for recipe in filtered_recipes:
                recipe_id = recipe['id']
                
                # Recipe card
                recipe_card = ctk.CTkFrame(
                    self.recipe_selection_frame,
                    fg_color=self.colors['bg_light'],
                    corner_radius=10
                )
                recipe_card.pack(fill="x", padx=10, pady=5)
                
                # Checkbox
                is_selected = recipe_id in self.selected_recipe_ids
                checkbox_var = ctk.BooleanVar(value=is_selected)
                
                checkbox = ctk.CTkCheckBox(
                    recipe_card,
                    text="",
                    variable=checkbox_var,
                    width=30,
                    command=lambda rid=recipe_id, var=checkbox_var: self.toggle_recipe_selection(rid, var)
                )
                checkbox.pack(side="left", padx=15, pady=15)
                
                # Recipe info
                info_frame = ctk.CTkFrame(recipe_card, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, pady=10)
                
                # Recipe name
                name_label = ctk.CTkLabel(
                    info_frame,
                    text=recipe['name'],
                    font=("Helvetica", 16, "bold"),
                    text_color="#1E90FF",
                    anchor="w"
                )
                name_label.pack(anchor="w")
                
                # Recipe details
                details = []
                if recipe.get('category'):
                    details.append(f"📁 {recipe['category']}")
                if recipe.get('servings'):
                    details.append(f"🍽️ {recipe['servings']}")
                
                # Get ingredient count
                ingredients = self.db.get_ingredients(recipe_id)
                details.append(f"🛒 {len(ingredients)} ingredients")
                
                details_text = " • ".join(details)
                details_label = ctk.CTkLabel(
                    info_frame,
                    text=details_text,
                    font=("Helvetica", 12),
                    text_color=self.colors['text_dark'],
                    anchor="w"
                )
                details_label.pack(anchor="w", pady=(5, 0))
        
        # Update count if label exists
        if hasattr(self, 'selected_count_label'):
            self.selected_count_label.configure(text=f"Selected: {len(self.selected_recipe_ids)} recipes")
    
    def toggle_recipe_selection(self, recipe_id, checkbox_var):
        """Toggle recipe selection"""
        if checkbox_var.get():
            self.selected_recipe_ids.add(recipe_id)
        else:
            self.selected_recipe_ids.discard(recipe_id)
        
        # Update count
        if hasattr(self, 'selected_count_label'):
            self.selected_count_label.configure(text=f"Selected: {len(self.selected_recipe_ids)} recipes")
    
    def select_all_recipes(self):
        """Select all visible recipes"""
        # Get search term
        search_term = ""
        if hasattr(self, 'list_search_entry'):
            search_term = self.list_search_entry.get().strip().lower()
        
        # Get all recipes
        all_recipes = self.db.get_all_recipes()
        
        # Filter by search term
        if search_term:
            filtered_recipes = [
                r for r in all_recipes 
                if search_term in r['name'].lower() or 
                (r['category'] and search_term in r['category'].lower())
            ]
        else:
            filtered_recipes = all_recipes
        
        # Add all filtered recipe IDs
        for recipe in filtered_recipes:
            self.selected_recipe_ids.add(recipe['id'])
        
        # Refresh display
        self.refresh_recipe_selection_list()
        self.update_status(f"Selected {len(self.selected_recipe_ids)} recipes")
    
    def clear_all_recipes(self):
        """Clear all recipe selections"""
        self.selected_recipe_ids.clear()
        self.refresh_recipe_selection_list()
        self.update_status("Cleared all selections")
    
    def generate_grocery_list(self):
        """Generate combined grocery list from selected recipes"""
        if not self.selected_recipe_ids:
            messagebox.showwarning("No Recipes", "Please select at least one recipe to generate a grocery list!")
            return
        
        try:
            # Create shopping list in database
            list_name = f"Grocery List - {datetime.now().strftime('%B %d, %Y')}"
            list_id = self.db.create_shopping_list(list_name, list(self.selected_recipe_ids))
            
            # Store current list ID
            self.current_grocery_list_id = list_id
            self.viewing_grocery_list = True
            
            # Show the generated list
            self.show_list_tab()
            self.update_status(f"Generated list from {len(self.selected_recipe_ids)} recipes")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate grocery list:\n{str(e)}")
            self.update_status("Error generating list")
    
    def display_generated_grocery_list(self):
        """Display the generated grocery list"""
        # Main container - don't let it expand
        main_container = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=750)
        main_container.pack(fill="x", padx=20, pady=10)
        main_container.pack_propagate(False)
        
        # Header with back button
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 15))
        
        back_btn = ctk.CTkButton(
            header_frame,
            text="← Back to Selection",
            font=("Helvetica", 14),
            width=150,
            height=35,
            fg_color=self.colors['accent'],
            command=self.return_to_recipe_selection
        )
        back_btn.pack(side="left")
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="🛒 Your Grocery List",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['primary']
        )
        title.pack(side="left", padx=20)
        
        # Get list items organized by category
        items = self.db.get_shopping_list_items(self.current_grocery_list_id, organized=True)
        
        # Recipe names section
        recipes_frame = ctk.CTkFrame(main_container, fg_color=self.colors['secondary'], corner_radius=10)
        recipes_frame.pack(fill="x", pady=(0, 10))
        
        recipes_title = ctk.CTkLabel(
            recipes_frame,
            text="� Recipes in this list:",
            font=("Helvetica", 16, "bold"),
            text_color="white"
        )
        recipes_title.pack(pady=(10, 8), padx=20, anchor="w")
        
        # Get and display recipe names
        for recipe_id in self.selected_recipe_ids:
            recipe = self.db.get_recipe(recipe_id)
            if recipe:
                recipe_label = ctk.CTkLabel(
                    recipes_frame,
                    text=f"  • {recipe['name']}",
                    font=("Helvetica", 13, "bold"),
                    text_color="#1E90FF",
                    anchor="w"
                )
                recipe_label.pack(pady=1, padx=20, anchor="w")
        
        # Add bottom padding
        ctk.CTkLabel(recipes_frame, text="", height=8).pack()
        
        # Info banner
        info_frame = ctk.CTkFrame(main_container, fg_color=self.colors['card_bg'], corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 8))
        
        info_text = f"📋 {len(items)} items"
        info_label = ctk.CTkLabel(
            info_frame,
            text=info_text,
            font=("Helvetica", 15),
            text_color=self.colors['text_dark']
        )
        info_label.pack(pady=10)
        
        # Scrollable list - Fixed height to keep buttons visible
        list_frame = ctk.CTkScrollableFrame(
            main_container,
            fg_color=self.colors['card_bg'],
            corner_radius=15,
            height=320
        )
        list_frame.pack(fill="x", pady=(0, 10))
        
        if not items:
            no_items = ctk.CTkLabel(
                list_frame,
                text="No items in this list",
                font=("Helvetica", 16),
                text_color=self.colors['text_dark']
            )
            no_items.pack(pady=50)
        else:
            # Organize items by category for display
            current_category = None
            
            for item in items:
                category = item.get('category', 'Other')
                if not category:
                    category = 'Other'
                
                # Show category header when it changes
                if category != current_category:
                    current_category = category
                    category_header = ctk.CTkLabel(
                        list_frame,
                        text=f"📦 {category}",
                        font=("Helvetica", 18, "bold"),
                        text_color=self.colors['primary'],
                        anchor="w"
                    )
                    category_header.pack(fill="x", padx=10, pady=(15, 10))
                
                # Item card
                item_card = ctk.CTkFrame(
                    list_frame,
                    fg_color=self.colors['bg_light'],
                    corner_radius=8
                )
                item_card.pack(fill="x", padx=10, pady=3)
                
                # Checkbox for marking as purchased
                is_checked = item.get('is_checked', 0) == 1
                checkbox_var = ctk.BooleanVar(value=is_checked)
                
                checkbox = ctk.CTkCheckBox(
                    item_card,
                    text="",
                    variable=checkbox_var,
                    width=30,
                    command=lambda item_id=item['id']: self.db.toggle_shopping_item(item_id)
                )
                checkbox.pack(side="left", padx=15, pady=10)
                
                # Item text
                item_text = item['ingredient_text']
                if item.get('quantity') and item.get('unit'):
                    item_text = f"{item['quantity']} {item['unit']} {item_text}"
                elif item.get('quantity'):
                    item_text = f"{item['quantity']} {item_text}"
                
                text_label = ctk.CTkLabel(
                    item_card,
                    text=item_text,
                    font=("Helvetica", 15),
                    text_color=self.colors['text_dark'],
                    anchor="w"
                )
                text_label.pack(side="left", fill="x", expand=True, padx=(0, 15))
        
        # Action buttons - Fixed section at bottom
        button_section = ctk.CTkFrame(main_container, fg_color="transparent")
        button_section.pack(fill="x", pady=(10, 0))
        
        button_frame = ctk.CTkFrame(button_section, fg_color="transparent")
        button_frame.pack()
        
        print_btn = ctk.CTkButton(
            button_frame,
            text="🖨️ Print List",
            font=("Helvetica", 18, "bold"),
            width=200,
            height=55,
            corner_radius=10,
            fg_color=self.colors['secondary'],
            hover_color="#E67E22",
            command=self.print_grocery_list
        )
        print_btn.pack(side="left", padx=10)
        
        new_list_btn = ctk.CTkButton(
            button_frame,
            text="✨ New List",
            font=("Helvetica", 18, "bold"),
            width=200,
            height=55,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color="#27AE60",
            command=self.create_new_grocery_list
        )
        new_list_btn.pack(side="left", padx=10)
    
    def return_to_recipe_selection(self):
        """Return to recipe selection view"""
        self.viewing_grocery_list = False
        self.show_list_tab()
    
    def create_new_grocery_list(self):
        """Create a new grocery list"""
        self.selected_recipe_ids.clear()
        self.viewing_grocery_list = False
        self.show_list_tab()
        self.update_status("Ready to create new list")
    
    def print_grocery_list(self):
        """Print grocery list"""
        if not hasattr(self, 'current_grocery_list_id'):
            messagebox.showwarning("No List", "No grocery list to print!")
            return
        
        try:
            items = self.db.get_shopping_list_items(self.current_grocery_list_id)
            
            # Generate HTML for printing
            html = self._generate_grocery_list_html(items)
            
            # Save to temporary file
            temp_html = Path("data") / "temp_grocery_list.html"
            temp_html.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html)
            
            # Open in browser
            import webbrowser
            webbrowser.open(f'file:///{temp_html.absolute()}')
            
            messagebox.showinfo(
                "Print Ready",
                f"Grocery list opened in your browser.\n\n"
                "Use Ctrl+P or the browser's print button to print."
            )
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not prepare list for printing:\n{str(e)}")
    
    def _generate_grocery_list_html(self, items):
        """Generate HTML for printing grocery list with recipe titles and categories"""
        now = datetime.now().strftime('%B %d, %Y')
        
        # Get recipe names for the selected recipes
        recipe_names = []
        for recipe_id in self.selected_recipe_ids:
            recipe = self.db.get_recipe(recipe_id)
            if recipe:
                recipe_names.append(recipe['name'])
        
        # Organize items by category
        categorized_items = {}
        for item in items:
            category = item.get('category', 'Other')
            if not category:
                category = 'Other'
            if category not in categorized_items:
                categorized_items[category] = []
            categorized_items[category].append(item)
        
        # Category order
        category_order = ['Produce', 'Meat & Poultry', 'Seafood', 'Dairy', 'Bakery', 'Frozen', 'Pantry', 'Other']
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Grocery List - {now}</title>
    <style>
        @media print {{
            @page {{ margin: 0.75in; }}
        }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2ECC71;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        h1 {{
            color: #2ECC71;
            margin: 0;
            font-size: 32px;
        }}
        .date {{
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }}
        .recipes-section {{
            background: #f0f9f4;
            border-left: 4px solid #2ECC71;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .recipes-title {{
            font-weight: bold;
            color: #2ECC71;
            margin-bottom: 10px;
            font-size: 18px;
        }}
        .recipe-name {{
            color: #1E90FF;
            font-size: 15px;
            font-weight: bold;
            margin: 5px 0;
            padding-left: 10px;
        }}
        .category-section {{
            margin: 30px 0;
        }}
        .category-title {{
            font-size: 20px;
            font-weight: bold;
            color: #2ECC71;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #2ECC71;
        }}
        .items {{
            list-style: none;
            padding: 0;
            margin: 0 0 20px 0;
        }}
        .item {{
            padding: 12px 15px;
            margin: 8px 0;
            background: #f8f8f8;
            border-radius: 8px;
            font-size: 16px;
            display: flex;
            align-items: center;
        }}
        .checkbox {{
            width: 20px;
            height: 20px;
            border: 2px solid #2ECC71;
            border-radius: 4px;
            margin-right: 15px;
            flex-shrink: 0;
        }}
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #999;
            font-size: 14px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🛒 Grocery List</h1>
        <div class="date">{now}</div>
        <div class="date">{len(items)} items from {len(self.selected_recipe_ids)} recipes</div>
    </div>
    
    <div class="recipes-section">
        <div class="recipes-title">📖 Recipes in this list:</div>
"""
        
        for recipe_name in recipe_names:
            html += f"""        <div class="recipe-name">• {recipe_name}</div>\n"""
        
        html += """    </div>
    
"""
        
        # Add items organized by category
        for category in category_order:
            if category in categorized_items:
                items_in_category = categorized_items[category]
                html += f"""    <div class="category-section">
        <div class="category-title">{category}</div>
        <ul class="items">
"""
                
                for item in items_in_category:
                    item_text = item['ingredient_text']
                    if item.get('quantity') and item.get('unit'):
                        item_text = f"{item['quantity']} {item['unit']} {item_text}"
                    elif item.get('quantity'):
                        item_text = f"{item['quantity']} {item_text}"
                    
                    html += f"""            <li class="item">
                <div class="checkbox"></div>
                <span>{item_text}</span>
            </li>
"""
                
                html += """        </ul>
    </div>
"""
        
        html += """    
    <div class="footer">
        Generated by Recipe Scanner Pro
    </div>
</body>
</html>"""
        
        return html
    
    def print_recipe(self, recipe_id):
        """Print a recipe with image (if available)"""
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Recipe not found!")
            return
        
        try:
            # Create HTML for printing
            html_content = self._generate_recipe_html(recipe)
            
            # Save to temporary HTML file
            temp_html = Path("data") / "temp_print.html"
            temp_html.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_html, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Open in default browser for printing
            import webbrowser
            webbrowser.open(f'file:///{temp_html.absolute()}')
            
            messagebox.showinfo(
                "Print Ready", 
                f"Recipe '{recipe['name']}' opened in your browser.\n\n"
                "Use Ctrl+P or the browser's print button to print.\n\n"
                "The page will include the recipe image if available."
            )
            
        except Exception as e:
            messagebox.showerror("Print Error", f"Could not prepare recipe for printing:\n{str(e)}")
    
    def _generate_recipe_html(self, recipe):
        """Generate HTML for printing a recipe"""
        # Start HTML
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        @media print {{
            @page {{ margin: 0.75in; }}
        }}
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 20px auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .recipe-header {{
            text-align: center;
            border-bottom: 3px solid #2ECC71;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .recipe-title {{
            font-size: 32px;
            font-weight: bold;
            color: #2ECC71;
            margin: 0 0 10px 0;
        }}
        .recipe-meta {{
            display: flex;
            justify-content: center;
            gap: 20px;
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }}
        .recipe-image {{
            text-align: center;
            margin: 30px 0;
        }}
        .recipe-image img {{
            max-width: 100%;
            max-height: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .section {{
            margin: 30px 0;
        }}
        .section-title {{
            font-size: 24px;
            font-weight: bold;
            color: #2C3E50;
            border-bottom: 2px solid #ECF0F1;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .ingredients-list {{
            list-style: none;
            padding: 0;
        }}
        .ingredients-list li {{
            padding: 8px 0;
            padding-left: 25px;
            position: relative;
        }}
        .ingredients-list li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #2ECC71;
            font-weight: bold;
        }}
        .instructions-list {{
            counter-reset: step-counter;
            list-style: none;
            padding: 0;
        }}
        .instructions-list li {{
            counter-increment: step-counter;
            padding: 15px 0;
            padding-left: 40px;
            position: relative;
            border-bottom: 1px solid #ECF0F1;
        }}
        .instructions-list li:before {{
            content: counter(step-counter);
            position: absolute;
            left: 0;
            top: 15px;
            background: #2ECC71;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }}
        .tags {{
            margin-top: 30px;
            padding: 15px;
            background: #F8F9FA;
            border-radius: 8px;
            text-align: center;
        }}
        .tag {{
            display: inline-block;
            background: #3498DB;
            color: white;
            padding: 5px 15px;
            margin: 5px;
            border-radius: 15px;
            font-size: 12px;
        }}
        @media print {{
            body {{
                margin: 0;
                padding: 20px;
            }}
            .recipe-image img {{
                max-height: 300px;
            }}
        }}
    </style>
</head>
<body>
    <div class="recipe-header">
        <h1 class="recipe-title">{title}</h1>
        <div class="recipe-meta">
""".format(title=recipe['name'])
        
        # Add metadata
        meta_items = []
        if recipe.get('category'):
            meta_items.append(f"<span>📂 {recipe['category']}</span>")
        if recipe.get('servings'):
            meta_items.append(f"<span>🍽️ {recipe['servings']} servings</span>")
        if recipe.get('prep_time'):
            meta_items.append(f"<span>⏱️ Prep: {recipe['prep_time']}</span>")
        if recipe.get('cook_time'):
            meta_items.append(f"<span>🔥 Cook: {recipe['cook_time']}</span>")
        
        html += '\n            '.join(meta_items)
        html += """
        </div>
    </div>
"""
        
        # Add image if available
        if recipe.get('image_path'):
            image_path = Path(recipe['image_path'])
            if image_path.exists():
                # Convert path to file:/// URL for HTML
                image_url = image_path.absolute().as_uri()
                html += f"""
    <div class="recipe-image">
        <img src="{image_url}" alt="{recipe['name']}">
    </div>
"""
        
        # Add ingredients
        html += """
    <div class="section">
        <h2 class="section-title">Ingredients</h2>
        <ul class="ingredients-list">
"""
        for ing in recipe.get('ingredients', []):
            html += f"            <li>{ing['ingredient_text']}</li>\n"
        
        html += """        </ul>
    </div>
"""
        
        # Add instructions
        html += """
    <div class="section">
        <h2 class="section-title">Instructions</h2>
        <ol class="instructions-list">
"""
        for inst in recipe.get('instructions', []):
            html += f"            <li>{inst['instruction_text']}</li>\n"
        
        html += """        </ol>
    </div>
"""
        
        # Add variations if available
        if recipe.get('variations'):
            html += """
    <div class="section">
        <h2 class="section-title">Variations</h2>
        <p style="padding-left: 10px; white-space: pre-wrap;">{variations}</p>
    </div>
""".format(variations=recipe['variations'])
        
        # Add notes if available
        if recipe.get('notes'):
            html += """
    <div class="section">
        <h2 class="section-title">Notes</h2>
        <p style="padding-left: 10px; white-space: pre-wrap;">{notes}</p>
    </div>
""".format(notes=recipe['notes'])
        
        # Add tags if available
        if recipe.get('tags'):
            html += """
    <div class="tags">
        <strong>Tags:</strong> 
"""
            for tag in recipe['tags']:
                html += f'        <span class="tag">{tag}</span>\n'
            html += """    </div>
"""
        
        # Close HTML
        html += """
</body>
</html>"""
        
        return html
    
    def show_settings(self):
        """Show settings dialog"""
        # Create settings dialog
        settings_dialog = ctk.CTkToplevel(self)
        settings_dialog.title("Settings")
        settings_dialog.geometry("580x800")
        settings_dialog.transient(self)
        settings_dialog.grab_set()
        
        # Main frame - NO SCROLLING
        main_frame = ctk.CTkFrame(settings_dialog, fg_color=self.colors['bg_light'])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            main_frame,
            text="⚙️ Manage Recipe Categories",
            font=("Helvetica", 18, "bold"),
            text_color=self.colors['secondary']
        )
        title.pack(pady=(0, 10))
        
        # Category list display
        list_label = ctk.CTkLabel(
            main_frame,
            text="Current Categories:",
            font=("Helvetica", 12, "bold"),
            text_color=self.colors['text_dark'],
            anchor="w"
        )
        list_label.pack(fill="x", padx=10, pady=(5, 3))
        
        # Textbox to display categories - SMALLER
        category_display = ctk.CTkTextbox(
            main_frame,
            width=500,
            height=120,
            font=("Helvetica", 11)
        )
        category_display.pack(padx=10, pady=(0, 10))
        
        def update_category_display():
            """Update the category list display"""
            category_display.delete("1.0", "end")
            for idx, cat in enumerate(sorted(self.category_options), 1):
                category_display.insert("end", f"{idx}. {cat}\n")
        
        # Initial display
        update_category_display()
        
        # Delete category section
        delete_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card_bg'], corner_radius=10, height=150)
        delete_frame.pack(fill="x", padx=10, pady=(0, 10))
        delete_frame.pack_propagate(False)  # Force the height
        
        delete_label = ctk.CTkLabel(
            delete_frame,
            text="🗑️ Delete Category:",
            font=("Helvetica", 13, "bold"),
            text_color=self.colors['text_dark']
        )
        delete_label.pack(padx=10, pady=(15, 8))
        
        delete_dropdown = ctk.CTkOptionMenu(
            delete_frame,
            values=sorted(self.category_options),
            width=450,
            height=35,
            font=("Helvetica", 12)
        )
        delete_dropdown.pack(padx=10, pady=(0, 8))
        
        def delete_selected_category():
            """Delete the selected category"""
            if len(self.category_options) <= 3:
                messagebox.showwarning("Cannot Delete", "You must have at least 3 categories!")
                return
            
            selected = delete_dropdown.get()
            result = messagebox.askyesno(
                "Confirm Delete",
                f"Delete category '{selected}'?"
            )
            
            if result:
                self.category_options.remove(selected)
                self.filter_categories = ["All"] + self.category_options
                
                # Update the dropdown
                delete_dropdown.configure(values=sorted(self.category_options))
                if self.category_options:
                    delete_dropdown.set(sorted(self.category_options)[0])
                
                update_category_display()
                messagebox.showinfo("Deleted", f"Category '{selected}' removed!")
        
        delete_btn = ctk.CTkButton(
            delete_frame,
            text="Delete Selected Category",
            width=450,
            height=40,
            font=("Helvetica", 12, "bold"),
            fg_color=self.colors['error'],
            hover_color="#c0392b",
            command=delete_selected_category
        )
        delete_btn.pack(padx=10, pady=(0, 15))
        
        # Add new category section
        add_frame = ctk.CTkFrame(main_frame, fg_color=self.colors['card_bg'], corner_radius=10, height=160)
        add_frame.pack(fill="x", padx=10, pady=(0, 10))
        add_frame.pack_propagate(False)  # Force the height
        
        add_label = ctk.CTkLabel(
            add_frame,
            text="➕ Add New Category:",
            font=("Helvetica", 13, "bold"),
            text_color=self.colors['text_dark']
        )
        add_label.pack(padx=10, pady=(15, 8))
        
        new_category_entry = ctk.CTkEntry(
            add_frame,
            placeholder_text="Enter category name",
            width=450,
            height=35,
            font=("Helvetica", 12)
        )
        new_category_entry.pack(padx=10, pady=(0, 8))
        
        def add_new_category():
            """Add a new category"""
            new_name = new_category_entry.get().strip()
            
            if not new_name:
                messagebox.showwarning("Empty Name", "Please enter a category name!")
                return
            
            if new_name in self.category_options:
                messagebox.showwarning("Duplicate", f"Category '{new_name}' already exists!")
                return
            
            if len(new_name) > 30:
                messagebox.showwarning("Too Long", "Category name must be 30 characters or less!")
                return
            
            # Add the category
            self.category_options.append(new_name)
            self.filter_categories = ["All"] + self.category_options
            
            # Update dropdown
            delete_dropdown.configure(values=sorted(self.category_options))
            
            # Clear entry and refresh
            new_category_entry.delete(0, 'end')
            update_category_display()
            messagebox.showinfo("Success", f"Category '{new_name}' added!")
        
        add_btn = ctk.CTkButton(
            add_frame,
            text="Add Category",
            width=450,
            height=40,
            font=("Helvetica", 12, "bold"),
            fg_color=self.colors['success'],
            hover_color="#27ae60",
            command=add_new_category
        )
        add_btn.pack(padx=10, pady=(0, 15))
        
        # Bind Enter key to add category
        new_category_entry.bind('<Return>', lambda e: add_new_category())
        
        # Close button - BIG and visible
        close_btn = ctk.CTkButton(
            main_frame,
            text="✓ Done",
            font=("Helvetica", 14, "bold"),
            width=450,
            height=45,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=settings_dialog.destroy
        )
        close_btn.pack(padx=10, pady=(10, 10))
    
    def show_manual_entry(self):
        """Show manual recipe entry form"""
        self.clear_content()
        self.update_status("Manual Entry")
        
        # Create scrollable form
        form_container = ctk.CTkScrollableFrame(self.content_frame, fg_color=self.colors['bg_light'])
        form_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            form_container,
            text="✍️ Add Recipe Manually",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['accent']
        )
        title.pack(pady=20)
        
        # Form frame
        form_frame = ctk.CTkFrame(form_container, fg_color=self.colors['card_bg'], corner_radius=15)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Recipe Name
        name_label = ctk.CTkLabel(form_frame, text="Recipe Name:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        name_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        name_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., Grandma's Chocolate Chip Cookies", width=600, height=40, font=("Helvetica", 14))
        name_entry.pack(pady=(0, 15), padx=20)
        
        # Category
        category_label = ctk.CTkLabel(form_frame, text="Category:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        category_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        category_dropdown = ctk.CTkOptionMenu(form_frame, values=self.category_options, width=300, height=40, font=("Helvetica", 14))
        category_dropdown.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Servings and Time
        details_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Servings
        servings_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        servings_container.pack(side="left", padx=(0, 20))
        
        servings_label = ctk.CTkLabel(servings_container, text="Servings:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        servings_label.pack(anchor="w", pady=(0, 5))
        
        servings_entry = ctk.CTkEntry(servings_container, placeholder_text="e.g., 4", width=150, height=40, font=("Helvetica", 14))
        servings_entry.pack()
        
        # Prep Time
        prep_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        prep_container.pack(side="left", padx=(0, 20))
        
        prep_label = ctk.CTkLabel(prep_container, text="Prep Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        prep_label.pack(anchor="w", pady=(0, 5))
        
        prep_entry = ctk.CTkEntry(prep_container, placeholder_text="e.g., 15 mins", width=150, height=40, font=("Helvetica", 14))
        prep_entry.pack()
        
        # Cook Time
        cook_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        cook_container.pack(side="left")
        
        cook_label = ctk.CTkLabel(cook_container, text="Cook Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        cook_label.pack(anchor="w", pady=(0, 5))
        
        cook_entry = ctk.CTkEntry(cook_container, placeholder_text="e.g., 30 mins", width=150, height=40, font=("Helvetica", 14))
        cook_entry.pack()
        
        # Ingredients
        ingredients_label = ctk.CTkLabel(form_frame, text="Ingredients (one per line):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        ingredients_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        ingredients_text = ctk.CTkTextbox(form_frame, width=600, height=200, font=("Helvetica", 14))
        ingredients_text.pack(pady=(0, 15), padx=20)
        ingredients_text.insert("1.0", "2 cups all-purpose flour\n1 cup sugar\n1/2 cup butter\n...")
        
        # Instructions
        instructions_label = ctk.CTkLabel(form_frame, text="Instructions:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        instructions_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        instructions_text = ctk.CTkTextbox(form_frame, width=600, height=300, font=("Helvetica", 14))
        instructions_text.pack(pady=(0, 15), padx=20)
        instructions_text.insert("1.0", "1. Preheat oven to 350°F\n2. Mix dry ingredients...\n3. Add wet ingredients...\n...")
        
        # Variations
        variations_label = ctk.CTkLabel(form_frame, text="Variations:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        variations_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        variations_text = ctk.CTkTextbox(form_frame, width=600, height=100, font=("Helvetica", 14))
        variations_text.pack(pady=(0, 15), padx=20)
        variations_text.insert("1.0", "Optional recipe modifications and alternatives...")
        
        # Notes
        notes_label = ctk.CTkLabel(form_frame, text="Notes:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        notes_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        notes_text = ctk.CTkTextbox(form_frame, width=600, height=100, font=("Helvetica", 14))
        notes_text.pack(pady=(0, 15), padx=20)
        notes_text.insert("1.0", "Personal cooking tips and reminders...")
        
        # Tags
        tags_label = ctk.CTkLabel(form_frame, text="Tags (comma-separated):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        tags_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        tags_entry = ctk.CTkEntry(form_frame, placeholder_text="e.g., vegetarian, quick, family-friendly", width=600, height=40, font=("Helvetica", 14))
        tags_entry.pack(pady=(0, 20), padx=20)
        
        # Buttons
        button_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        button_frame.pack(pady=20)
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Recipe",
            font=("Helvetica", 18, "bold"),
            width=200,
            height=50,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=lambda: self.save_manual_recipe(
                name_entry.get(),
                category_dropdown.get(),
                servings_entry.get(),
                prep_entry.get(),
                cook_entry.get(),
                ingredients_text.get("1.0", "end-1c"),
                instructions_text.get("1.0", "end-1c"),
                variations_text.get("1.0", "end-1c"),
                notes_text.get("1.0", "end-1c"),
                tags_entry.get()
            )
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            font=("Helvetica", 18, "bold"),
            width=150,
            height=50,
            corner_radius=10,
            fg_color=self.colors['accent'],
            command=self.show_home_tab
        )
        cancel_btn.pack(side="left", padx=10)
    
    def save_manual_recipe(self, name, category, servings, prep_time, cook_time, ingredients, instructions, variations, notes, tags):
        """Save manually entered recipe"""
        if not name:
            messagebox.showwarning("Missing Info", "Please enter a recipe name!")
            return
        
        if not ingredients.strip():
            messagebox.showwarning("Missing Info", "Please enter ingredients!")
            return
        
        if not instructions.strip():
            messagebox.showwarning("Missing Info", "Please enter instructions!")
            return
        
        try:
            # Parse ingredients and instructions
            ingredient_list = [line.strip() for line in ingredients.split('\n') if line.strip()]
            instruction_list = [line.strip() for line in instructions.split('\n') if line.strip()]
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Save to database
            recipe_id = self.db.add_recipe(
                name=name,
                category=category,
                servings=servings,
                prep_time=prep_time,
                cook_time=cook_time,
                ingredients=ingredient_list,
                instructions=instruction_list,
                tags=tag_list,
                source='manual',
                variations=variations.strip(),
                notes=notes.strip()
            )
            
            messagebox.showinfo("Success", f"Recipe '{name}' saved successfully!\n\nRecipe ID: {recipe_id}")
            self.update_status(f"Saved: {name}")
            self.update_recipe_count()
            self.show_home_tab()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save recipe:\n{str(e)}")
            self.update_status("Error saving recipe")
    
    def create_recipe_card(self, parent, recipe):
        """Create a recipe card widget"""
        card = ctk.CTkFrame(parent, fg_color=self.colors['card_bg'], corner_radius=10)
        
        # Main content container (horizontal layout with image on left)
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="x", padx=15, pady=10)
        
        # Image thumbnail (if available)
        if recipe.get('image_path') and Path(recipe['image_path']).exists():
            try:
                # Load and resize image
                img = Image.open(recipe['image_path'])
                img.thumbnail((120, 120))
                photo = ctk.CTkImage(light_image=img, dark_image=img, size=(120, 120))
                
                image_label = ctk.CTkLabel(content_frame, image=photo, text="")
                image_label.pack(side="left", padx=(0, 15))
                # Keep reference to prevent garbage collection
                image_label.image = photo
            except Exception as e:
                print(f"Error loading image: {e}")
        
        # Recipe info (right side)
        info_container = ctk.CTkFrame(content_frame, fg_color="transparent")
        info_container.pack(side="left", fill="both", expand=True)
        
        info_frame = ctk.CTkFrame(info_container, fg_color="transparent")
        info_frame.pack(fill="x")
        
        # Title with favorite star
        title_text = recipe['name']
        if recipe.get('is_favorite'):
            title_text = f"⭐ {title_text}"
        
        name_label = ctk.CTkLabel(
            info_frame,
            text=title_text,
            font=("Helvetica", 18, "bold"),
            text_color="#1E90FF",
            anchor="w"
        )
        name_label.pack(side="left", fill="x", expand=True)
        
        # Category badge
        if recipe.get('category'):
            category_badge = ctk.CTkLabel(
                info_frame,
                text=recipe['category'],
                font=("Helvetica", 12),
                fg_color=self.colors['secondary'],
                text_color="white",
                corner_radius=5,
                padx=10,
                pady=5
            )
            category_badge.pack(side="right", padx=5)
        
        # Details
        details = []
        if recipe.get('servings'):
            details.append(f"🍽️ {recipe['servings']}")
        if recipe.get('prep_time'):
            details.append(f"⏱️ {recipe['prep_time']}")
        if recipe.get('rating', 0) > 0:
            stars = "⭐" * recipe['rating']
            details.append(stars)
        
        if details:
            details_label = ctk.CTkLabel(
                info_container,
                text=" | ".join(details),
                font=("Helvetica", 12),
                text_color=self.colors['text_dark'],
                anchor="w"
            )
            details_label.pack(fill="x", pady=(5, 0))
        
        # Buttons
        button_frame = ctk.CTkFrame(card, fg_color="transparent")
        button_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        view_btn = ctk.CTkButton(
            button_frame,
            text="👁️ View",
            width=80,
            height=30,
            font=("Helvetica", 12),
            fg_color=self.colors['primary'],
            command=lambda: self.view_recipe(recipe['id'])
        )
        view_btn.pack(side="left", padx=2)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Edit",
            width=80,
            height=30,
            font=("Helvetica", 12),
            fg_color=self.colors['secondary'],
            command=lambda: self.edit_recipe(recipe['id'])
        )
        edit_btn.pack(side="left", padx=2)
        
        # Add "View Image" button if recipe has an image
        if recipe.get('image_path') and Path(recipe['image_path']).exists():
            image_btn = ctk.CTkButton(
                button_frame,
                text="🖼️ Image",
                width=80,
                height=30,
                font=("Helvetica", 12),
                fg_color=self.colors['success'],
                command=lambda: self.view_recipe_image(recipe['id'])
            )
            image_btn.pack(side="left", padx=2)
        
        print_btn = ctk.CTkButton(
            button_frame,
            text="🖨️ Print",
            width=80,
            height=30,
            font=("Helvetica", 12),
            fg_color=self.colors['warning'],
            command=lambda: self.print_recipe(recipe['id'])
        )
        print_btn.pack(side="left", padx=2)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Delete",
            width=80,
            height=30,
            font=("Helvetica", 12),
            fg_color=self.colors['accent'],
            command=lambda: self.delete_recipe_confirm(recipe['id'], recipe['name'])
        )
        delete_btn.pack(side="left", padx=2)
        
        return card
    
    def view_recipe(self, recipe_id):
        """View recipe details"""
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Recipe not found!")
            return
        
        # Create a new top-level window instead of messagebox
        dialog = ctk.CTkToplevel(self)
        dialog.title(recipe['name'])
        dialog.geometry("900x700")
        dialog.transient(self)
        
        # Title
        title = ctk.CTkLabel(
            dialog,
            text=f"📖 {recipe['name']}",
            font=("Arial", 20, "bold"),
            text_color=self.colors['secondary']
        )
        title.pack(pady=15)
        
        # Text frame
        text_frame = ctk.CTkFrame(dialog)
        text_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Format recipe details for display
        details = f"Category: {recipe.get('category', 'N/A')}\n"
        details += f"Servings: {recipe.get('servings', 'N/A')}\n"
        details += f"Prep Time: {recipe.get('prep_time', 'N/A')}\n"
        details += f"Cook Time: {recipe.get('cook_time', 'N/A')}\n\n"
        
        details += "INGREDIENTS:\n"
        for ing in recipe.get('ingredients', []):
            details += f"• {ing['ingredient_text']}\n"
        
        details += "\nINSTRUCTIONS:\n"
        for inst in recipe.get('instructions', []):
            details += f"{inst['step_number']}. {inst['instruction_text']}\n"
        
        if recipe.get('variations'):
            details += f"\nVARIATIONS:\n{recipe['variations']}\n"
        
        if recipe.get('notes'):
            details += f"\nNOTES:\n{recipe['notes']}\n"
        
        if recipe.get('tags'):
            details += f"\nTags: {', '.join(recipe['tags'])}\n"
        
        # Textbox with recipe details - larger font
        text_box = ctk.CTkTextbox(
            text_frame,
            font=("Arial", 14),
            wrap="word"
        )
        text_box.pack(fill="both", expand=True, padx=5, pady=5)
        text_box.insert("1.0", details)
        
        # Close button
        close_btn = ctk.CTkButton(
            dialog,
            text="Close",
            font=("Arial", 14, "bold"),
            width=150,
            height=40,
            fg_color=self.colors['accent'],
            command=dialog.destroy
        )
        close_btn.pack(pady=(0, 15))
    
    def edit_recipe(self, recipe_id):
        """Edit recipe"""
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Recipe not found!")
            return
        
        self.clear_content()
        self.update_status(f"Editing: {recipe['name']}")
        
        # Create scrollable form
        form_container = ctk.CTkScrollableFrame(self.content_frame, fg_color=self.colors['bg_light'])
        form_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        # Title
        title = ctk.CTkLabel(
            form_container,
            text="✏️ Edit Recipe",
            font=("Helvetica", 28, "bold"),
            text_color=self.colors['secondary']
        )
        title.pack(pady=20)
        
        # Recipe Name
        name_label = ctk.CTkLabel(form_container, text="Recipe Name:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        name_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        name_entry = ctk.CTkEntry(form_container, width=600, height=40, font=("Helvetica", 14))
        name_entry.insert(0, recipe.get('name', ''))
        name_entry.pack(pady=(0, 15), padx=20)
        
        # Category
        category_label = ctk.CTkLabel(form_container, text="Category:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        category_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        category_dropdown = ctk.CTkOptionMenu(form_container, values=self.category_options, width=300, height=40, font=("Helvetica", 14))
        current_category = recipe.get('category', 'Main Course')
        if current_category in self.category_options:
            category_dropdown.set(current_category)
        category_dropdown.pack(pady=(0, 15), padx=20, anchor="w")
        
        # Servings and Time
        details_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        details_frame.pack(fill="x", padx=20, pady=10)
        
        # Servings
        servings_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        servings_container.pack(side="left", padx=(0, 20))
        
        servings_label = ctk.CTkLabel(servings_container, text="Servings:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        servings_label.pack(anchor="w", pady=(0, 5))
        
        servings_entry = ctk.CTkEntry(servings_container, width=150, height=40, font=("Helvetica", 14))
        servings_entry.insert(0, recipe.get('servings', ''))
        servings_entry.pack()
        
        # Prep Time
        prep_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        prep_container.pack(side="left", padx=(0, 20))
        
        prep_label = ctk.CTkLabel(prep_container, text="Prep Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        prep_label.pack(anchor="w", pady=(0, 5))
        
        prep_entry = ctk.CTkEntry(prep_container, width=150, height=40, font=("Helvetica", 14))
        prep_entry.insert(0, recipe.get('prep_time', ''))
        prep_entry.pack()
        
        # Cook Time
        cook_container = ctk.CTkFrame(details_frame, fg_color="transparent")
        cook_container.pack(side="left")
        
        cook_label = ctk.CTkLabel(cook_container, text="Cook Time:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        cook_label.pack(anchor="w", pady=(0, 5))
        
        cook_entry = ctk.CTkEntry(cook_container, width=150, height=40, font=("Helvetica", 14))
        cook_entry.insert(0, recipe.get('cook_time', ''))
        cook_entry.pack()
        
        # Ingredients
        ingredients_label = ctk.CTkLabel(form_container, text="Ingredients (one per line):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        ingredients_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        ingredients_text = ctk.CTkTextbox(form_container, width=600, height=150, font=("Helvetica", 14))
        ingredients_content = '\n'.join([ing['ingredient_text'] for ing in recipe.get('ingredients', [])])
        ingredients_text.insert("1.0", ingredients_content)
        ingredients_text.pack(pady=(0, 15), padx=20)
        
        # Instructions
        instructions_label = ctk.CTkLabel(form_container, text="Instructions:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        instructions_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        instructions_text = ctk.CTkTextbox(form_container, width=600, height=200, font=("Helvetica", 14))
        instructions_content = '\n\n'.join([inst['instruction_text'] for inst in recipe.get('instructions', [])])
        instructions_text.insert("1.0", instructions_content)
        instructions_text.pack(pady=(0, 15), padx=20)
        
        # Variations
        variations_label = ctk.CTkLabel(form_container, text="Variations:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        variations_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        variations_text = ctk.CTkTextbox(form_container, width=600, height=80, font=("Helvetica", 14))
        variations_content = recipe.get('variations') or ''
        variations_text.insert("1.0", variations_content)
        variations_text.pack(pady=(0, 15), padx=20)
        
        # Notes
        notes_label = ctk.CTkLabel(form_container, text="Notes:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        notes_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        notes_text = ctk.CTkTextbox(form_container, width=600, height=80, font=("Helvetica", 14))
        notes_content = recipe.get('notes') or ''
        notes_text.insert("1.0", notes_content)
        notes_text.pack(pady=(0, 15), padx=20)
        
        # Tags
        tags_label = ctk.CTkLabel(form_container, text="Tags (comma-separated):", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        tags_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        tags_entry = ctk.CTkEntry(form_container, width=600, height=40, font=("Helvetica", 14))
        tags_content = ', '.join(recipe.get('tags', []))
        tags_entry.insert(0, tags_content)
        tags_entry.pack(pady=(0, 20), padx=20)
        
        # Image section
        image_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        image_frame.pack(pady=(10, 20), padx=20)
        
        image_label = ctk.CTkLabel(image_frame, text="Recipe Image:", font=("Helvetica", 16, "bold"), text_color=self.colors['text_dark'])
        image_label.pack(side="left", padx=(0, 10))
        
        # Show current image status
        if recipe.get('image_path') and Path(recipe['image_path']).exists():
            status_text = "✓ Image attached"
            view_img_btn = ctk.CTkButton(
                image_frame,
                text="👁️ View Image",
                width=120,
                height=35,
                fg_color=self.colors['secondary'],
                command=lambda: self.view_recipe_image(recipe_id)
            )
            view_img_btn.pack(side="left", padx=5)
        else:
            status_text = "No image"
        
        status_label = ctk.CTkLabel(image_frame, text=status_text, font=("Helvetica", 14), text_color=self.colors['text_dark'])
        status_label.pack(side="left", padx=10)
        
        add_img_btn = ctk.CTkButton(
            image_frame,
            text="🖼️ Add/Change Image",
            width=160,
            height=35,
            fg_color=self.colors['primary'],
            command=lambda: self.add_or_change_recipe_image(recipe_id)
        )
        add_img_btn.pack(side="left", padx=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(form_container, fg_color="transparent")
        button_frame.pack(pady=(20, 40))
        
        save_btn = ctk.CTkButton(
            button_frame,
            text="💾 Save Changes",
            font=("Helvetica", 18, "bold"),
            width=200,
            height=50,
            corner_radius=10,
            fg_color=self.colors['primary'],
            hover_color=self.colors['success'],
            command=lambda: self.save_recipe_changes(
                recipe_id,
                name_entry.get(),
                category_dropdown.get(),
                servings_entry.get(),
                prep_entry.get(),
                cook_entry.get(),
                ingredients_text.get("1.0", "end-1c"),
                instructions_text.get("1.0", "end-1c"),
                variations_text.get("1.0", "end-1c"),
                notes_text.get("1.0", "end-1c"),
                tags_entry.get()
            )
        )
        save_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            font=("Helvetica", 18, "bold"),
            width=150,
            height=50,
            corner_radius=10,
            fg_color=self.colors['accent'],
            command=self.show_browse_tab
        )
        cancel_btn.pack(side="left", padx=10)
        
        # Add spacer at bottom to ensure scroll works
        spacer = ctk.CTkLabel(form_container, text="", height=100)
        spacer.pack()
        
        # Force update to ensure scroll region is calculated correctly
        form_container.update_idletasks()
    
    def save_recipe_changes(self, recipe_id, name, category, servings, prep_time, cook_time, ingredients, instructions, variations, notes, tags):
        """Save changes to an existing recipe"""
        if not name:
            messagebox.showwarning("Missing Info", "Please enter a recipe name!")
            return
        
        if not ingredients.strip():
            messagebox.showwarning("Missing Info", "Please enter ingredients!")
            return
        
        if not instructions.strip():
            messagebox.showwarning("Missing Info", "Please enter instructions!")
            return
        
        try:
            # Update recipe basic info
            self.db.update_recipe(
                recipe_id,
                name=name,
                category=category,
                servings=servings,
                prep_time=prep_time,
                cook_time=cook_time,
                variations=variations.strip(),
                notes=notes.strip()
            )
            
            # Delete old ingredients and instructions
            old_ingredients = self.db.get_ingredients(recipe_id)
            for ing in old_ingredients:
                self.db.delete_ingredient(ing['id'])
            
            old_instructions = self.db.get_instructions(recipe_id)
            for inst in old_instructions:
                self.db.delete_instruction(inst['id'])
            
            # Delete old tags
            old_tags = self.db.get_tags(recipe_id)
            for tag in old_tags:
                self.db.delete_tag(recipe_id, tag)
            
            # Add new ingredients
            ingredient_list = [line.strip() for line in ingredients.split('\n') if line.strip()]
            for idx, ingredient in enumerate(ingredient_list):
                self.db.add_ingredient(recipe_id, ingredient, position=idx)
            
            # Add new instructions
            instruction_list = [line.strip() for line in instructions.split('\n') if line.strip()]
            for idx, instruction in enumerate(instruction_list, start=1):
                self.db.add_instruction(recipe_id, idx, instruction)
            
            # Add new tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            for tag in tag_list:
                self.db.add_tag(recipe_id, tag)
            
            messagebox.showinfo("Success", f"Recipe '{name}' updated successfully!")
            self.update_status(f"Updated: {name}")
            self.show_browse_tab()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update recipe:\n{str(e)}")
            self.update_status("Error updating recipe")
    
    def add_or_change_recipe_image(self, recipe_id):
        """Add or change the image for a recipe"""
        recipe = self.db.get_recipe(recipe_id)
        if not recipe:
            messagebox.showerror("Error", "Recipe not found!")
            return
        
        # Ask user to select an image file
        file_path = filedialog.askopenfilename(
            title="Select Recipe Image",
            filetypes=[
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create images directory if it doesn't exist
            images_dir = Path("data/images")
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy image to data/images with recipe ID in filename
            source_path = Path(file_path)
            file_extension = source_path.suffix
            dest_filename = f"recipe_{recipe_id}_{source_path.stem}{file_extension}"
            dest_path = images_dir / dest_filename
            
            # Copy the file
            import shutil
            shutil.copy2(file_path, dest_path)
            
            # Update database with new image path
            self.db.update_recipe(recipe_id, image_path=str(dest_path))
            
            messagebox.showinfo("Success", f"Image added to '{recipe['name']}'!")
            self.update_status(f"Image added to: {recipe['name']}")
            
            # Refresh the current view
            self.show_browse_tab()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add image:\n{str(e)}")
    
    def view_recipe_image(self, recipe_id):
        """View recipe image in a larger window"""
        recipe = self.db.get_recipe(recipe_id)
        if not recipe or not recipe.get('image_path'):
            messagebox.showinfo("No Image", "This recipe doesn't have an image.")
            return
        
        image_path = Path(recipe['image_path'])
        if not image_path.exists():
            messagebox.showerror("Error", "Image file not found!")
            return
        
        try:
            # Create popup window
            popup = ctk.CTkToplevel(self)
            popup.title(f"Image: {recipe['name']}")
            popup.geometry("800x600")
            
            # Load and display image
            img = Image.open(image_path)
            # Resize to fit window while maintaining aspect ratio
            img.thumbnail((750, 550))
            photo = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            
            image_label = ctk.CTkLabel(popup, image=photo, text="")
            image_label.pack(pady=20, padx=20)
            
            # Keep reference to prevent garbage collection
            image_label.image = photo
            
            # Close button
            close_btn = ctk.CTkButton(
                popup,
                text="Close",
                command=popup.destroy,
                width=100,
                height=40
            )
            close_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image:\n{str(e)}")
    
    def delete_recipe_confirm(self, recipe_id, recipe_name):
        """Confirm and delete recipe"""
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{recipe_name}'?\n\nThis cannot be undone!"
        )
        if result:
            try:
                self.db.delete_recipe(recipe_id)
                messagebox.showinfo("Deleted", f"Recipe '{recipe_name}' has been deleted.")
                self.update_status(f"Deleted: {recipe_name}")
                self.update_recipe_count()
                self.show_browse_tab()  # Refresh browse view
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete recipe:\n{str(e)}")
    

def main():
    """Main entry point"""
    app = RecipeScannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
