"""
Database Manager for Recipe Scanner Pro
Handles all SQLite database operations
"""

import sqlite3
import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from fractions import Fraction


class DatabaseManager:
    """Manages recipe database operations"""
    
    def __init__(self, db_path: str = "data/recipes.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.cursor = self.connection.cursor()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        
        # Recipes table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                servings TEXT,
                prep_time TEXT,
                cook_time TEXT,
                total_time TEXT,
                source TEXT DEFAULT 'manual',
                image_path TEXT,
                variations TEXT,
                notes TEXT,
                is_favorite INTEGER DEFAULT 0,
                date_added TEXT NOT NULL,
                date_modified TEXT NOT NULL,
                times_made INTEGER DEFAULT 0,
                rating INTEGER DEFAULT 0
            )
        """)
        
        # Ingredients table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS ingredients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                ingredient_text TEXT NOT NULL,
                quantity TEXT,
                unit TEXT,
                ingredient_name TEXT,
                notes TEXT,
                position INTEGER DEFAULT 0,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        
        # Instructions table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS instructions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                step_number INTEGER NOT NULL,
                instruction_text TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        
        # Tags table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipe_id INTEGER NOT NULL,
                tag_name TEXT NOT NULL,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
            )
        """)
        
        # Pantry table (for ingredient matching)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS pantry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ingredient_name TEXT NOT NULL UNIQUE,
                quantity TEXT,
                unit TEXT,
                date_added TEXT NOT NULL,
                expiry_date TEXT
            )
        """)
        
        # Shopping lists table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_name TEXT NOT NULL,
                date_created TEXT NOT NULL,
                is_completed INTEGER DEFAULT 0
            )
        """)
        
        # Shopping list items table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS shopping_list_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                list_id INTEGER NOT NULL,
                ingredient_text TEXT NOT NULL,
                quantity TEXT,
                unit TEXT,
                category TEXT DEFAULT '',
                is_checked INTEGER DEFAULT 0,
                FOREIGN KEY (list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE
            )
        """)
        
        self.connection.commit()
        
        # Migrate existing databases - add missing columns if they don't exist
        self._migrate_database()
    
    def _migrate_database(self):
        """Add any missing columns to existing databases"""
        try:
            # Check if variations column exists in recipes
            self.cursor.execute("PRAGMA table_info(recipes)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'variations' not in columns:
                self.cursor.execute("ALTER TABLE recipes ADD COLUMN variations TEXT")
                self.connection.commit()
                print("Database migrated: Added 'variations' column to recipes table")
            
            # Check if category column exists in shopping_list_items
            self.cursor.execute("PRAGMA table_info(shopping_list_items)")
            columns = [column[1] for column in self.cursor.fetchall()]
            
            if 'category' not in columns:
                self.cursor.execute("ALTER TABLE shopping_list_items ADD COLUMN category TEXT DEFAULT ''")
                self.connection.commit()
                print("Database migrated: Added 'category' column to shopping_list_items table")
        except Exception as e:
            print(f"Migration check: {e}")
    
    # ========== RECIPE OPERATIONS ==========
    
    def add_recipe(self, name: str, category: str = "", servings: str = "",
                   prep_time: str = "", cook_time: str = "", ingredients: List[str] = None,
                   instructions: List[str] = None, tags: List[str] = None,
                   source: str = "manual", image_path: str = "", variations: str = "", notes: str = "") -> int:
        """
        Add a new recipe to the database
        Returns the recipe ID
        """
        now = datetime.now().isoformat()
        
        # Calculate total time if both prep and cook are provided
        total_time = self._calculate_total_time(prep_time, cook_time)
        
        # Insert recipe
        self.cursor.execute("""
            INSERT INTO recipes (name, category, servings, prep_time, cook_time, 
                               total_time, source, image_path, variations, notes, date_added, date_modified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, category, servings, prep_time, cook_time, total_time, 
              source, image_path, variations, notes, now, now))
        
        recipe_id = self.cursor.lastrowid
        
        # Add ingredients
        if ingredients:
            for idx, ingredient in enumerate(ingredients):
                self.add_ingredient(recipe_id, ingredient, position=idx)
        
        # Add instructions
        if instructions:
            for idx, instruction in enumerate(instructions, start=1):
                self.add_instruction(recipe_id, idx, instruction)
        
        # Add tags
        if tags:
            for tag in tags:
                self.add_tag(recipe_id, tag.strip())
        
        self.connection.commit()
        return recipe_id
    
    def get_recipe(self, recipe_id: int) -> Optional[Dict]:
        """Get a single recipe by ID with all details"""
        self.cursor.execute("SELECT * FROM recipes WHERE id = ?", (recipe_id,))
        recipe = self.cursor.fetchone()
        
        if not recipe:
            return None
        
        # Convert to dictionary
        recipe_dict = dict(recipe)
        
        # Add ingredients
        recipe_dict['ingredients'] = self.get_ingredients(recipe_id)
        
        # Add instructions
        recipe_dict['instructions'] = self.get_instructions(recipe_id)
        
        # Add tags
        recipe_dict['tags'] = self.get_tags(recipe_id)
        
        return recipe_dict
    
    def get_all_recipes(self, search: str = "", category: str = "", 
                       favorite_only: bool = False) -> List[Dict]:
        """Get all recipes with optional filtering"""
        query = "SELECT * FROM recipes WHERE 1=1"
        params = []
        
        if search:
            query += " AND name LIKE ?"
            params.append(f"%{search}%")
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        if favorite_only:
            query += " AND is_favorite = 1"
        
        query += " ORDER BY date_added DESC"
        
        self.cursor.execute(query, params)
        recipes = self.cursor.fetchall()
        
        # Convert to list of dictionaries
        return [dict(recipe) for recipe in recipes]
    
    def update_recipe(self, recipe_id: int, **kwargs):
        """Update recipe fields"""
        kwargs['date_modified'] = datetime.now().isoformat()
        
        # Build UPDATE query dynamically
        fields = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [recipe_id]
        
        self.cursor.execute(f"UPDATE recipes SET {fields} WHERE id = ?", values)
        self.connection.commit()
    
    def delete_recipe(self, recipe_id: int):
        """Delete a recipe and all associated data"""
        self.cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        self.connection.commit()
    
    def toggle_favorite(self, recipe_id: int):
        """Toggle favorite status of a recipe"""
        self.cursor.execute("SELECT is_favorite FROM recipes WHERE id = ?", (recipe_id,))
        result = self.cursor.fetchone()
        if result:
            new_status = 0 if result[0] else 1
            self.cursor.execute("UPDATE recipes SET is_favorite = ? WHERE id = ?", 
                              (new_status, recipe_id))
            self.connection.commit()
    
    def increment_times_made(self, recipe_id: int):
        """Increment the times_made counter"""
        self.cursor.execute("UPDATE recipes SET times_made = times_made + 1 WHERE id = ?", 
                          (recipe_id,))
        self.connection.commit()
    
    def set_rating(self, recipe_id: int, rating: int):
        """Set recipe rating (1-5 stars)"""
        rating = max(0, min(5, rating))  # Clamp between 0 and 5
        self.cursor.execute("UPDATE recipes SET rating = ? WHERE id = ?", 
                          (rating, recipe_id))
        self.connection.commit()
    
    # ========== INGREDIENT OPERATIONS ==========
    
    def add_ingredient(self, recipe_id: int, ingredient_text: str, 
                      quantity: str = "", unit: str = "", 
                      ingredient_name: str = "", notes: str = "", position: int = 0):
        """Add an ingredient to a recipe"""
        self.cursor.execute("""
            INSERT INTO ingredients (recipe_id, ingredient_text, quantity, unit, 
                                   ingredient_name, notes, position)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (recipe_id, ingredient_text, quantity, unit, ingredient_name, notes, position))
        self.connection.commit()
    
    def get_ingredients(self, recipe_id: int) -> List[Dict]:
        """Get all ingredients for a recipe"""
        self.cursor.execute("""
            SELECT * FROM ingredients 
            WHERE recipe_id = ? 
            ORDER BY position
        """, (recipe_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_ingredient(self, ingredient_id: int, **kwargs):
        """Update an ingredient"""
        fields = ", ".join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [ingredient_id]
        self.cursor.execute(f"UPDATE ingredients SET {fields} WHERE id = ?", values)
        self.connection.commit()
    
    def delete_ingredient(self, ingredient_id: int):
        """Delete an ingredient"""
        self.cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
        self.connection.commit()
    
    # ========== INSTRUCTION OPERATIONS ==========
    
    def add_instruction(self, recipe_id: int, step_number: int, instruction_text: str):
        """Add an instruction step to a recipe"""
        self.cursor.execute("""
            INSERT INTO instructions (recipe_id, step_number, instruction_text)
            VALUES (?, ?, ?)
        """, (recipe_id, step_number, instruction_text))
        self.connection.commit()
    
    def get_instructions(self, recipe_id: int) -> List[Dict]:
        """Get all instructions for a recipe"""
        self.cursor.execute("""
            SELECT * FROM instructions 
            WHERE recipe_id = ? 
            ORDER BY step_number
        """, (recipe_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def update_instruction(self, instruction_id: int, instruction_text: str):
        """Update an instruction"""
        self.cursor.execute("""
            UPDATE instructions SET instruction_text = ? WHERE id = ?
        """, (instruction_text, instruction_id))
        self.connection.commit()
    
    def delete_instruction(self, instruction_id: int):
        """Delete an instruction"""
        self.cursor.execute("DELETE FROM instructions WHERE id = ?", (instruction_id,))
        self.connection.commit()
    
    # ========== TAG OPERATIONS ==========
    
    def add_tag(self, recipe_id: int, tag_name: str):
        """Add a tag to a recipe"""
        self.cursor.execute("""
            INSERT INTO tags (recipe_id, tag_name)
            VALUES (?, ?)
        """, (recipe_id, tag_name))
        self.connection.commit()
    
    def get_tags(self, recipe_id: int) -> List[str]:
        """Get all tags for a recipe"""
        self.cursor.execute("SELECT tag_name FROM tags WHERE recipe_id = ?", (recipe_id,))
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags in the database"""
        self.cursor.execute("SELECT DISTINCT tag_name FROM tags ORDER BY tag_name")
        return [row[0] for row in self.cursor.fetchall()]
    
    def delete_tag(self, recipe_id: int, tag_name: str):
        """Delete a tag from a recipe"""
        self.cursor.execute("""
            DELETE FROM tags WHERE recipe_id = ? AND tag_name = ?
        """, (recipe_id, tag_name))
        self.connection.commit()
    
    # ========== STATISTICS ==========
    
    def get_statistics(self) -> Dict:
        """Get recipe database statistics"""
        stats = {}
        
        # Total recipes
        self.cursor.execute("SELECT COUNT(*) FROM recipes")
        stats['total_recipes'] = self.cursor.fetchone()[0]
        
        # Favorites
        self.cursor.execute("SELECT COUNT(*) FROM recipes WHERE is_favorite = 1")
        stats['favorites'] = self.cursor.fetchone()[0]
        
        # Recipes by category
        self.cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM recipes 
            GROUP BY category 
            ORDER BY count DESC
        """)
        stats['by_category'] = {row[0]: row[1] for row in self.cursor.fetchall()}
        
        # Recently added (last 7 days)
        self.cursor.execute("""
            SELECT COUNT(*) FROM recipes 
            WHERE date_added >= date('now', '-7 days')
        """)
        stats['added_this_week'] = self.cursor.fetchone()[0]
        
        # Most made recipes
        self.cursor.execute("""
            SELECT name, times_made FROM recipes 
            WHERE times_made > 0 
            ORDER BY times_made DESC 
            LIMIT 5
        """)
        stats['most_made'] = [dict(name=row[0], count=row[1]) 
                              for row in self.cursor.fetchall()]
        
        # Total tags
        self.cursor.execute("SELECT COUNT(DISTINCT tag_name) FROM tags")
        stats['total_tags'] = self.cursor.fetchone()[0]
        
        return stats
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        self.cursor.execute("SELECT DISTINCT category FROM recipes WHERE category != '' ORDER BY category")
        return [row[0] for row in self.cursor.fetchall()]
    
    # ========== SEARCH AND MATCH ==========
    
    def search_recipes_by_ingredients(self, ingredient_list: List[str]) -> List[Dict]:
        """Find recipes that contain any of the given ingredients"""
        if not ingredient_list:
            return []
        
        # Build query with multiple ingredient searches
        placeholders = " OR ".join(["ingredient_text LIKE ?" for _ in ingredient_list])
        params = [f"%{ing}%" for ing in ingredient_list]
        
        self.cursor.execute(f"""
            SELECT DISTINCT r.*, 
                   COUNT(i.id) as matching_ingredients
            FROM recipes r
            JOIN ingredients i ON r.id = i.recipe_id
            WHERE {placeholders}
            GROUP BY r.id
            ORDER BY matching_ingredients DESC, r.name
        """, params)
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    # ========== PANTRY OPERATIONS ==========
    
    def add_to_pantry(self, ingredient_name: str, quantity: str = "", 
                     unit: str = "", expiry_date: str = "") -> int:
        """Add an ingredient to pantry"""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute("""
                INSERT INTO pantry (ingredient_name, quantity, unit, date_added, expiry_date)
                VALUES (?, ?, ?, ?, ?)
            """, (ingredient_name, quantity, unit, now, expiry_date))
            self.connection.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            # Ingredient already exists, update it
            self.cursor.execute("""
                UPDATE pantry SET quantity = ?, unit = ?, expiry_date = ?
                WHERE ingredient_name = ?
            """, (quantity, unit, expiry_date, ingredient_name))
            self.connection.commit()
            return 0
    
    def get_pantry_items(self) -> List[Dict]:
        """Get all pantry items"""
        self.cursor.execute("SELECT * FROM pantry ORDER BY ingredient_name")
        return [dict(row) for row in self.cursor.fetchall()]
    
    def remove_from_pantry(self, pantry_id: int):
        """Remove item from pantry"""
        self.cursor.execute("DELETE FROM pantry WHERE id = ?", (pantry_id,))
        self.connection.commit()
    
    # ========== SHOPPING LIST OPERATIONS ==========
    
    def create_shopping_list(self, list_name: str, recipe_ids: List[int] = None) -> int:
        """Create a new shopping list from recipes with smart consolidation"""
        now = datetime.now().isoformat()
        
        self.cursor.execute("""
            INSERT INTO shopping_lists (list_name, date_created)
            VALUES (?, ?)
        """, (list_name, now))
        list_id = self.cursor.lastrowid
        
        if recipe_ids:
            # Collect all ingredients from selected recipes with smart consolidation
            ingredients_map = self._consolidate_ingredients(recipe_ids)
            
            # Add to shopping list
            for ing_data in ingredients_map.values():
                self.cursor.execute("""
                    INSERT INTO shopping_list_items (list_id, ingredient_text, quantity, unit, category)
                    VALUES (?, ?, ?, ?, ?)
                """, (list_id, ing_data['text'], ing_data['quantity'], ing_data['unit'], ing_data.get('category', '')))
        
        self.connection.commit()
        return list_id
    
    def _consolidate_ingredients(self, recipe_ids: List[int]) -> Dict:
        """Smart ingredient consolidation with quantity addition and categorization"""
        from fractions import Fraction
        import re
        
        ingredients_map = {}
        
        for recipe_id in recipe_ids:
            ingredients = self.get_ingredients(recipe_id)
            for ing in ingredients:
                text = ing['ingredient_text'].strip()
                quantity_str = ing.get('quantity', '').strip()
                unit = ing.get('unit', '').strip()
                
                # Normalize ingredient name for matching
                normalized_name = self._normalize_ingredient_name(text)
                
                # Create key for matching (normalized name + unit)
                key = f"{normalized_name}_{unit.lower()}"
                
                if key in ingredients_map:
                    # Ingredient exists - try to add quantities
                    existing = ingredients_map[key]
                    combined_qty = self._add_quantities(existing['quantity'], quantity_str)
                    existing['quantity'] = combined_qty
                    existing['count'] += 1
                else:
                    # New ingredient
                    category = self._categorize_ingredient(text)
                    ingredients_map[key] = {
                        'text': text,
                        'quantity': quantity_str,
                        'unit': unit,
                        'category': category,
                        'count': 1
                    }
        
        return ingredients_map
    
    def _normalize_ingredient_name(self, text: str) -> str:
        """Normalize ingredient name for matching"""
        # Remove common descriptors
        text = re.sub(r'\b(fresh|frozen|dried|chopped|diced|sliced|minced|grated|shredded|canned)\b', '', text, flags=re.IGNORECASE)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip().lower()
        return text
    
    def _add_quantities(self, qty1: str, qty2: str) -> str:
        """Add two quantity strings (supports fractions and decimals)"""
        if not qty1 and not qty2:
            return ''
        if not qty1:
            return qty2
        if not qty2:
            return qty1
        
        try:
            # Convert to fractions for accurate addition
            from fractions import Fraction
            
            # Parse first quantity
            val1 = self._parse_quantity(qty1)
            val2 = self._parse_quantity(qty2)
            
            if val1 is None or val2 is None:
                # Can't parse, keep separate
                return f"{qty1} + {qty2}"
            
            # Add them
            total = val1 + val2
            
            # Convert back to string (prefer fractions for common values)
            if total == int(total):
                return str(int(total))
            elif total.denominator in [2, 3, 4, 8]:
                return str(total)
            else:
                return f"{float(total):.2f}".rstrip('0').rstrip('.')
        
        except:
            # Fallback - keep separate
            return f"{qty1} + {qty2}"
    
    def _parse_quantity(self, qty_str: str):
        """Parse quantity string to Fraction"""
        from fractions import Fraction
        import re
        
        if not qty_str:
            return None
        
        qty_str = qty_str.strip()
        
        # Handle mixed numbers like "1 1/2"
        mixed_match = re.match(r'(\d+)\s+(\d+)/(\d+)', qty_str)
        if mixed_match:
            whole = int(mixed_match.group(1))
            num = int(mixed_match.group(2))
            denom = int(mixed_match.group(3))
            return Fraction(whole) + Fraction(num, denom)
        
        # Handle simple fractions like "1/2"
        if '/' in qty_str:
            try:
                return Fraction(qty_str)
            except:
                pass
        
        # Handle decimals and integers
        try:
            return Fraction(float(qty_str))
        except:
            return None
    
    def _categorize_ingredient(self, text: str) -> str:
        """Categorize ingredient by type"""
        text_lower = text.lower()
        
        # Dairy (check first for eggs, milk, cheese, etc.)
        dairy = ['egg', 'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream', 'cottage cheese',
                 'whipped cream', 'half and half', 'heavy cream', 'yolk', 'white', 'buttermilk',
                 'parmesan', 'cheddar', 'mozzarella', 'feta', 'ricotta', 'cream cheese']
        if any(item in text_lower for item in dairy):
            return 'Dairy'
        
        # Produce
        produce = ['lettuce', 'tomato', 'onion', 'garlic', 'potato', 'carrot', 'celery', 'pepper', 
                   'apple', 'banana', 'lemon', 'lime', 'orange', 'spinach', 'kale', 'cucumber',
                   'avocado', 'mushroom', 'zucchini', 'broccoli', 'cauliflower', 'cabbage',
                   'corn', 'peas', 'bean', 'berry', 'berries', 'peach', 'grape', 'melon',
                   'squash', 'eggplant', 'radish', 'beet', 'turnip', 'parsley', 'cilantro',
                   'basil', 'mint', 'thyme', 'rosemary', 'dill', 'chive', 'scallion', 'shallot',
                   'ginger', 'jalapeno', 'serrano', 'poblano', 'bell pepper', 'cherry', 'strawberry',
                   'blueberry', 'raspberry', 'blackberry', 'pineapple', 'mango', 'papaya', 'kiwi',
                   'plum', 'pear', 'nectarine', 'apricot', 'watermelon', 'cantaloupe', 'honeydew',
                   'green bean', 'snap pea', 'snow pea', 'asparagus', 'artichoke', 'brussels sprout']
        if any(item in text_lower for item in produce):
            return 'Produce'
        
        # Meat & Poultry
        meat = ['chicken', 'beef', 'pork', 'turkey', 'lamb', 'sausage', 'bacon', 'ham',
                'ground beef', 'steak', 'roast', 'chop', 'breast', 'thigh', 'wing', 'drumstick',
                'tenderloin', 'sirloin', 'ribeye', 'brisket', 'ribs', 'ground turkey',
                'ground pork', 'ground chicken', 'veal', 'duck', 'goose', 'venison']
        if any(item in text_lower for item in meat):
            return 'Meat & Poultry'
        
        # Seafood
        seafood = ['fish', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'cod', 'tilapia',
                   'halibut', 'scallop', 'clam', 'mussel', 'oyster', 'trout', 'bass', 'catfish',
                   'mahi', 'snapper', 'swordfish', 'anchovy', 'sardine', 'mackerel', 'herring',
                   'squid', 'calamari', 'octopus', 'prawns']
        if any(item in text_lower for item in seafood):
            return 'Seafood'
        
        # Bakery
        bakery = ['bread', 'roll', 'bun', 'bagel', 'tortilla', 'pita', 'croissant', 'muffin',
                  'biscuit', 'pastry', 'english muffin', 'naan', 'flatbread', 'ciabatta',
                  'sourdough', 'rye bread', 'whole wheat bread', 'white bread', 'french bread',
                  'italian bread', 'baguette', 'pumpernickel', 'focaccia']
        if any(item in text_lower for item in bakery):
            return 'Bakery'
        
        # Frozen
        frozen = ['frozen', 'ice cream', 'popsicle', 'sherbet', 'sorbet', 'gelato']
        if any(item in text_lower for item in frozen):
            return 'Frozen'
        
        # Pantry/Dry Goods (check after more specific categories)
        pantry = ['flour', 'sugar', 'salt', 'pepper', 'rice', 'pasta', 'oil', 'vinegar',
                  'sauce', 'soup', 'broth', 'stock', 'can', 'canned', 'spice', 'seasoning',
                  'baking powder', 'baking soda', 'vanilla', 'extract', 'honey', 'syrup',
                  'molasses', 'cornstarch', 'cocoa', 'chocolate chip', 'nut', 'almond',
                  'walnut', 'pecan', 'cashew', 'peanut', 'peanut butter', 'almond butter',
                  'tahini', 'jam', 'jelly', 'preserves', 'maple syrup', 'corn syrup',
                  'brown sugar', 'powdered sugar', 'confectioners', 'granulated sugar',
                  'olive oil', 'vegetable oil', 'canola oil', 'coconut oil', 'sesame oil',
                  'balsamic', 'red wine vinegar', 'white vinegar', 'apple cider vinegar',
                  'soy sauce', 'worcestershire', 'hot sauce', 'ketchup', 'mustard', 'mayo',
                  'mayonnaise', 'relish', 'pickle', 'tomato paste', 'tomato sauce',
                  'chicken broth', 'beef broth', 'vegetable broth', 'bouillon', 'noodle',
                  'spaghetti', 'penne', 'macaroni', 'linguine', 'fettuccine', 'lasagna',
                  'quinoa', 'couscous', 'bulgur', 'barley', 'oat', 'cereal', 'granola',
                  'cracker', 'chip', 'pretzel', 'popcorn', 'cookie', 'brownie', 'cake mix',
                  'yeast', 'gelatin', 'cornmeal', 'breadcrumb', 'panko']
        if any(item in text_lower for item in pantry):
            return 'Pantry'
        
        # Default
        return 'Other'
    
    def get_shopping_lists(self) -> List[Dict]:
        """Get all shopping lists"""
        self.cursor.execute("""
            SELECT sl.*, COUNT(sli.id) as item_count
            FROM shopping_lists sl
            LEFT JOIN shopping_list_items sli ON sl.id = sli.list_id
            GROUP BY sl.id
            ORDER BY sl.date_created DESC
        """)
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_shopping_list_items(self, list_id: int, organized: bool = False) -> List[Dict]:
        """Get all items in a shopping list, optionally organized by category"""
        if organized:
            # Return items organized by category
            self.cursor.execute("""
                SELECT * FROM shopping_list_items 
                WHERE list_id = ? 
                ORDER BY 
                    CASE category
                        WHEN 'Produce' THEN 1
                        WHEN 'Meat & Poultry' THEN 2
                        WHEN 'Seafood' THEN 3
                        WHEN 'Dairy' THEN 4
                        WHEN 'Bakery' THEN 5
                        WHEN 'Frozen' THEN 6
                        WHEN 'Pantry' THEN 7
                        ELSE 8
                    END,
                    ingredient_text
            """, (list_id,))
        else:
            self.cursor.execute("""
                SELECT * FROM shopping_list_items WHERE list_id = ? ORDER BY id
            """, (list_id,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def toggle_shopping_item(self, item_id: int):
        """Toggle checked status of shopping list item"""
        self.cursor.execute("""
            UPDATE shopping_list_items 
            SET is_checked = CASE WHEN is_checked = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        """, (item_id,))
        self.connection.commit()
    
    def delete_shopping_list(self, list_id: int):
        """Delete a shopping list"""
        self.cursor.execute("DELETE FROM shopping_lists WHERE id = ?", (list_id,))
        self.connection.commit()
    
    # ========== UTILITY METHODS ==========
    
    def _calculate_total_time(self, prep_time: str, cook_time: str) -> str:
        """Calculate total time from prep and cook times (simple string concatenation)"""
        if prep_time and cook_time:
            return f"{prep_time} + {cook_time}"
        return prep_time or cook_time or ""
    
    def backup_database(self, backup_path: str = None):
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"data/backups/recipes_backup_{timestamp}.db"
        
        backup_file = Path(backup_path)
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        
        import shutil
        shutil.copy2(self.db_path, backup_file)
        return str(backup_file)
    
    def export_to_json(self, output_path: str):
        """Export all recipes to JSON file"""
        recipes = self.get_all_recipes()
        
        # Add full details for each recipe
        for recipe in recipes:
            recipe_id = recipe['id']
            recipe['ingredients'] = self.get_ingredients(recipe_id)
            recipe['instructions'] = self.get_instructions(recipe_id)
            recipe['tags'] = self.get_tags(recipe_id)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, indent=2, ensure_ascii=False)
    
    def import_from_json(self, json_path: str) -> int:
        """Import recipes from JSON file"""
        with open(json_path, 'r', encoding='utf-8') as f:
            recipes = json.load(f)
        
        imported_count = 0
        for recipe in recipes:
            try:
                # Extract data
                ingredients = recipe.pop('ingredients', [])
                instructions = recipe.pop('instructions', [])
                tags = recipe.pop('tags', [])
                
                # Remove ID to create new recipe
                recipe.pop('id', None)
                
                # Add recipe
                recipe_id = self.add_recipe(
                    name=recipe.get('name', 'Untitled'),
                    category=recipe.get('category', ''),
                    servings=recipe.get('servings', ''),
                    prep_time=recipe.get('prep_time', ''),
                    cook_time=recipe.get('cook_time', ''),
                    ingredients=[ing['ingredient_text'] for ing in ingredients],
                    instructions=[inst['instruction_text'] for inst in instructions],
                    tags=tags,
                    source=recipe.get('source', 'imported'),
                    notes=recipe.get('notes', '')
                )
                imported_count += 1
            except Exception as e:
                print(f"Error importing recipe: {e}")
                continue
        
        return imported_count
