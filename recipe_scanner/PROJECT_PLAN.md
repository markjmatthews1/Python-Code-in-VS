# 📚 Recipe Scanner & Manager System - Project Plan

## Project Overview
A free, offline recipe management system using HP scanner integration, OCR text extraction, and smart ingredient matching.

**Status**: 🚀 **PHASE 4 - ACTIVE DEVELOPMENT**  
**Last Updated**: October 31, 2025  
**Version**: 1.0 Beta

---

## 🎯 Core Features Progress

### 1. **Scanner Integration** 📄 ✅ COMPLETE
- ✅ Interface with HP scanner via Windows WIA
- ✅ Preview scan before processing
- ✅ Import existing images from file system
- ✅ Save scanned images to local folder (data/scanned_images/)
- ✅ Windows native scan dialog integration

### 2. **OCR Text Extraction** 🔍 ✅ COMPLETE
- ✅ Install and configure Tesseract OCR (user installation pending)
- ✅ Extract text from scanned recipe images with confidence scoring
- ✅ Clean and normalize extracted text
- ✅ Auto-enhance image quality (contrast, sharpness, grayscale, threshold)
- ✅ Manual text editing in OCR results form

### 3. **Recipe Parsing** 📝 ✅ COMPLETE
- ✅ Rule-based parser to identify:
  - ✅ Recipe title (first line detection)
  - ✅ Ingredients section (regex patterns with measurements)
  - ✅ Instructions section (numbered steps detection)
  - ✅ Servings, prep time, cook time (multiple format patterns)
- ✅ Structured data storage (SQLite database)
- ✅ Ingredient quantity extraction (1 cup, 2 tbsp, etc.)
- ✅ Manual edit mode for corrections (full edit form)

### 4. **Recipe Database** 💾 ✅ COMPLETE
- ✅ SQLite database for recipe storage (7 tables)
- ✅ Tables: recipes, ingredients, instructions, tags, pantry, shopping_lists, shopping_list_items
- ✅ Fields: name, category, servings, prep/cook time, rating, favorite, times_made, source, notes
- ✅ Auto-created on first run (data/recipes.db)
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ⏳ Auto-backup functionality (planned)
- ⏳ Import/Export recipes (JSON) (planned)

### 5. **Ingredient Matching Engine** 🔎 ✅ COMPLETE
- ✅ Input available ingredients (tag-based interface)
- ✅ Fuzzy ingredient matching with normalization
- ✅ Show recipes sorted by % of ingredients you have
- ✅ Three match categories: Can Make Now (100%), Almost There (70%+), Partial Matches (30%+)
- ✅ Highlight missing ingredients per recipe
- ✅ Match details breakdown (have/need lists)
- ✅ Smart normalization (removes measurements, quantities, descriptors)
- ⏳ Suggest substitutions (common swaps) (planned)

### 6. **Recipe Browser** 📖 ✅ COMPLETE
- ✅ View all recipes in card grid view
- ✅ Recipe cards show: name, category, servings, prep time, rating, favorite star
- ✅ 10 category filters: All, Appetizer, Main Course, Dessert, Breakfast, Soup, Salad, Side Dish, Beverage, Snack
- ✅ View full recipe with all details (popup)
- ✅ Edit recipe functionality (pre-populated form)
- ✅ Delete recipe with confirmation
- ✅ Print recipe (preview + direct printing)
- ⏳ Search by recipe name (UI ready, not connected)
- ⏳ Filter by dietary tags (planned)
- ⏳ Recipe images in cards (planned)

### 7. **Grocery List Generator** 📝 ⏳ IN PROGRESS
- ⏳ Select multiple recipes
- ⏳ Generate combined ingredient list
- ⏳ Remove duplicates and combine quantities
- ⏳ Organize by category (Produce, Dairy, Meat, etc.)
- ⏳ Print-friendly format
- ⏳ Export to text/PDF

### 8. **Desktop GUI Interface** 🖥️ ✅ COMPLETE
- ✅ CustomTkinter modern, colorful UI
- ✅ 5-tab navigation (Home, Scan, Browse, Match, List)
- ✅ Colorful gradient theme (Green, Blue, Orange, Red accents)
- ✅ Modern card-based layouts
- ✅ Icon-based buttons (emoji icons)
- ✅ Responsive layout with scrollable frames
- ✅ Status bar with real-time statistics
- ✅ All text minimum 12pt font
- ⏳ Dark/Light theme toggle (planned)

### 9. **Recipe Printing** 🖨️ ✅ COMPLETE (Just Added!)
- ✅ Print button on Browse tab recipe cards
- ✅ Print button on Match tab recipe cards
- ✅ Print preview window with full recipe details
- ✅ Direct printing to default Windows printer
- ✅ Copy to clipboard functionality
- ✅ Save as text file (.txt)
- ✅ Formatted output with sections and separators

---

## 📁 Project Structure (Current)

```
recipe_scanner/
│
├── app.py                      # ✅ Main CustomTkinter application (2061 lines)
├── requirements.txt            # ✅ Python dependencies
├── README.md                   # ✅ User documentation
├── PROJECT_PLAN.md             # ✅ This file
│
├── scanner/
│   ├── __init__.py            # ✅
│   └── scanner_interface.py   # ✅ Windows WIA scanner control (300+ lines)
│
├── ocr/
│   ├── __init__.py            # ✅
│   └── ocr_engine.py          # ✅ Tesseract OCR wrapper (400+ lines)
│
├── database/
│   ├── __init__.py            # ✅
│   └── db_manager.py          # ✅ SQLite operations (500+ lines)
│
├── matcher/
│   ├── __init__.py            # ✅
│   └── ingredient_matcher.py  # ✅ Fuzzy matching engine (300+ lines)
│
├── utils/                      # ⏳ To be created
│   ├── __init__.py
│   ├── grocery_list.py        # ⏳ Grocery list generation
│   └── pdf_generator.py       # ⏳ PDF formatting
│
├── data/
│   ├── recipes.db             # ✅ SQLite database (auto-created)
│   ├── scanned_images/        # ✅ Original scans
│   └── backups/               # ✅ Folder created (backup logic pending)
│
└── config/
    └── settings.json          # ⏳ App configuration (planned)
```

---

## 🛠️ Technology Stack

### Core Technologies ✅
- **Python 3.12.10**
- **CustomTkinter 5.2.2** - Modern, colorful GUI framework
- **tkinter** - Base GUI (included with Python)
- **SQLite** - Local database

### Scanner & OCR ✅
- **pywin32 306** - Windows scanner interface (WIA)
- **Tesseract OCR** - Free OCR engine (user needs to install)
- **pytesseract 0.3.10** - Python wrapper for Tesseract
- **Pillow (PIL)** - Image processing

### Data Processing ✅
- **pandas 2.1.3** - Data manipulation
- **re (regex)** - Pattern matching for parsing
- **difflib** - Fuzzy string matching

### Printing & Export
- **reportlab 4.0.7** - PDF generation (installed, not yet used)
- **Windows print commands** - Direct printer integration ✅

### Executable Compilation ⏳
- **PyInstaller 6.2.0** - Convert Python to .exe (ready to use)

---

## 📝 Development Phases

### Phase 1: Core Functionality ✅ COMPLETE
1. ✅ Project setup and structure
2. ✅ Scanner interface (scan to image)
3. ✅ OCR integration (image to text)
4. ✅ Basic recipe parsing with intelligent structure detection
5. ✅ SQLite database setup with 7 tables
6. ✅ CustomTkinter desktop GUI (5 tabs)

### Phase 2: Recipe Management ✅ COMPLETE
1. ✅ Recipe browser with card grid layout
2. ✅ Manual recipe entry form with validation
3. ✅ Recipe editing capabilities (full form with pre-population)
4. ✅ Category system (10 categories)
5. ✅ Recipe view with formatted details
6. ✅ Recipe deletion with confirmation
7. ✅ Tag system support

### Phase 3: Smart Features ✅ MOSTLY COMPLETE
1. ✅ Ingredient matcher with fuzzy matching
2. ✅ Match percentage categorization (100%, 70%+, 30%+)
3. ✅ Smart ingredient normalization
4. ⏳ Grocery list generator (next task)
5. ⏳ Ingredient substitutions (planned)

### Phase 4: Polish & Enhancements 🚀 ACTIVE
1. ✅ Recipe printing with direct printer support
2. ✅ Print preview with full recipe details
3. ✅ Copy to clipboard functionality
4. ✅ Save recipe as text file
5. ⏳ PDF export for grocery lists
6. ⏳ Settings & preferences dialog
7. ⏳ Search functionality (UI ready)
8. ⏳ Category filter actions (UI ready)
9. ⏳ User documentation refinement
10. ⏳ Auto-start with Windows (shortcut created)

---

## 🎯 Remaining Tasks

### High Priority 🔴
1. **Grocery List Generator** - Last major feature
   - Multi-select recipes from database
   - Combine ingredients with quantity consolidation
   - Organize by category (produce, dairy, meat, etc.)
   - Print/PDF export
   
2. **Connect Search Functionality** - Browse tab has search bar but not functional
   - Filter recipes as user types
   - Search by name, ingredients, or tags

3. **Connect Category Filters** - Browse tab has category buttons but not functional
   - Click category to filter recipe grid
   - Highlight selected category

### Medium Priority 🟡
4. **Tesseract OCR Installation Guide** - Help user install Tesseract
   - In-app instructions with download link
   - Path configuration
   - Test OCR with sample recipe

5. **Database Backup** - Auto-backup functionality
   - Scheduled backups (weekly/monthly)
   - Manual backup button
   - Restore from backup

6. **Settings Dialog** - App preferences
   - Scanner configuration
   - Database location
   - OCR settings
   - Theme preferences

### Low Priority 🟢
7. **Recipe Import/Export** - JSON format
   - Export selected recipes
   - Import from JSON file
   - Bulk operations

8. **Recipe Images in Cards** - Show scanned image thumbnails
   - Display in recipe cards
   - Gallery view option

9. **PyInstaller Compilation** - Create standalone .exe
   - Test compilation
   - Create icon
   - Distribution package

10. **Enhanced Features**
    - Recipe rating system (database ready)
    - Favorite toggle (database ready)
    - Times made counter (database ready)
    - Recipe notes (database ready)
    - Dark theme toggle

---

## 🎨 Current Color Scheme

```
Primary: #2ECC71 (Green - Fresh/Food) - Main actions, success
Secondary: #3498DB (Blue - Clean/Modern) - Secondary actions
Accent: #E74C3C (Red - Action buttons) - Delete, cancel
Warning: #F39C12 (Orange) - Cautions, warnings, print
Success: #27AE60 (Dark Green) - Confirmations
Background Light: #ECF0F1 (Light Gray)
Background Dark: #2C3E50 (Dark Blue-Gray)
Text Dark: #2C3E50
Card Background: #FFFFFF (White)
```

---

## ✅ Completed Features Summary

### Scanning & OCR ✅
- Windows native scan dialog
- Image import from file
- Tesseract OCR integration with confidence scoring
- Image preprocessing (resize, contrast, sharpness, grayscale)
- Intelligent recipe structure parsing
- Editable OCR results form

### Recipe Management ✅
- Add recipes manually or from scan
- Edit any recipe field
- Delete with confirmation
- View full recipe details
- Category system (10 categories)
- Tag support
- Rating, favorite, times made tracking
- Source tracking (manual/scanned)

### Ingredient Matching ✅
- Tag-based ingredient entry
- Fuzzy matching with normalization
- Match percentage calculation
- Three-tier categorization (100%, 70%+, 30%+)
- Missing ingredients list
- Match details breakdown

### User Interface ✅
- Modern CustomTkinter GUI
- 5 tabs: Home, Scan, Browse, Match, List
- Colorful card-based layouts
- Real-time statistics dashboard
- Scrollable frames throughout
- Minimum 12pt font everywhere
- Icon-based navigation
- Status bar

### Printing ✅
- Print button on all recipe cards
- Print preview window
- Direct printing to Windows printer
- Copy to clipboard
- Save as text file
- Formatted output with sections

---

## 📊 Database Schema (Implemented)

### Recipes Table ✅
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT,
    servings TEXT,
    prep_time TEXT,
    cook_time TEXT,
    source TEXT,
    image_path TEXT,
    is_favorite INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 0,
    times_made INTEGER DEFAULT 0,
    notes TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ingredients Table ✅
```sql
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    ingredient_text TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    sort_order INTEGER,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
```

### Instructions Table ✅
```sql
CREATE TABLE instructions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    step_number INTEGER NOT NULL,
    instruction_text TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
```

### Tags Table ✅
```sql
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    tag_name TEXT NOT NULL,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
);
```

### Pantry Table ✅
```sql
CREATE TABLE pantry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE,
    quantity TEXT,
    unit TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Shopping Lists Tables ✅
```sql
CREATE TABLE shopping_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_name TEXT NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shopping_list_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER,
    ingredient_name TEXT NOT NULL,
    quantity TEXT,
    unit TEXT,
    is_purchased INTEGER DEFAULT 0,
    FOREIGN KEY (list_id) REFERENCES shopping_lists(id) ON DELETE CASCADE
);
```

---

## 🚀 Next Steps (In Order)

1. **Implement Grocery List Generator** 🔴
   - Create `utils/grocery_list.py` module
   - Add recipe selection UI in List tab
   - Combine and deduplicate ingredients
   - Display organized list
   - Add print functionality

2. **Connect Search and Filters** 🟡
   - Wire up search bar in Browse tab
   - Connect category filter buttons
   - Add real-time filtering

3. **Test Complete Workflow** 🟡
   - Install Tesseract OCR
   - Scan real recipe
   - Test OCR parsing
   - Verify ingredient matching
   - Test grocery list generation

4. **Create Standalone Executable** 🟢
   - Test PyInstaller compilation
   - Create application icon
   - Bundle dependencies
   - Test on clean Windows system

---

## 📖 Installation Status

### Installed ✅
- Python 3.12.10
- CustomTkinter 5.2.2
- pywin32 306
- pytesseract 0.3.10
- Pillow
- pandas 2.1.3
- reportlab 4.0.7
- PyInstaller 6.2.0

### User Action Required ⏳
- **Tesseract OCR Executable** - Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Install to: `C:\Program Files\Tesseract-OCR\`
  - OCR will work once installed

---

## 🎉 Success Metrics

- ✅ Successfully scan and import recipes (OCR ready, pending Tesseract)
- ✅ Manual recipe entry in < 2 minutes
- ✅ Search recipes by ingredient with fuzzy matching
- ⏳ Generate grocery list for 5 recipes (next task)
- ⏳ Print grocery list in organized format (next task)
- ✅ Print individual recipes
- ✅ User-friendly interface (no coding knowledge needed)
- ✅ Modern, colorful desktop GUI
- ✅ Full CRUD operations working

---

**Last Updated**: October 31, 2025  
**Version**: 1.0 Beta  
**Status**: 🚀 Phase 4 Active Development - 85% Complete  
**Next Milestone**: Grocery List Generator

---

## 🔧 Installation Requirements

### System Requirements
- Windows 10/11 (for WIA scanner support)
- Python 3.10 or higher
- HP Scanner (connected and working)
- 500MB free disk space

### Software Dependencies
```bash
pip install customtkinter
pip install pytesseract
pip install Pillow
pip install pandas
pip install pywin32
pip install reportlab
pip install pyinstaller
```

### External Software
- **Tesseract OCR**: Download from https://github.com/UB-Mannheim/tesseract/wiki
  - Install to: `C:\Program Files\Tesseract-OCR\`
  - Add to PATH

### Compilation to EXE
```bash
# Simple one-file executable
pyinstaller --onefile --windowed --icon=icon.ico app.py

# Or with auto-py-to-exe GUI tool
pip install auto-py-to-exe
auto-py-to-exe
```

---

## 📊 Database Schema

### Recipes Table
```sql
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    ingredients TEXT NOT NULL,           -- JSON array
    instructions TEXT NOT NULL,
    servings TEXT,
    prep_time TEXT,
    cook_time TEXT,
    total_time TEXT,
    category TEXT,                       -- Appetizer, Main Course, Dessert, etc.
    cuisine TEXT,                        -- Italian, Mexican, Asian, etc.
    dietary_tags TEXT,                   -- JSON array: vegetarian, gluten-free, etc.
    source TEXT,                         -- Book name, website, handwritten, etc.
    image_path TEXT,                     -- Path to scanned image
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    rating INTEGER                       -- 1-5 stars
);
```

### Ingredients Table (for fast searching)
```sql
CREATE TABLE ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    ingredient_name TEXT,
    quantity TEXT,
    unit TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes (id)
);
```

### User Pantry Table
```sql
CREATE TABLE pantry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT UNIQUE,
    quantity TEXT,
    unit TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## 🎨 UI Design Mockup (Desktop GUI)

### Color Scheme
```
Primary: #2ECC71 (Green - Fresh/Food)
Secondary: #3498DB (Blue - Clean/Modern)
Accent: #E74C3C (Red - Action buttons)
Background: #ECF0F1 (Light Gray)
Dark Mode: #2C3E50 (Dark Blue-Gray)
Text: #2C3E50 (Dark) / #ECF0F1 (Light on dark)
```

### Main Window Layout
```
┌─────────────────────────────────────────────────────────┐
│  🍳 Recipe Scanner Pro          [─][□][×]               │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [🏠 Home] [📷 Scan] [📖 Browse] [🔎 Match] [📝 List]  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│                                                          │
│               MAIN CONTENT AREA                         │
│            (Tab-based navigation)                       │
│                                                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│  Status: Ready | 📚 Recipes: 45 | ⚙️ Settings | 🌓     │
└─────────────────────────────────────────────────────────┘
```

### Tab Views

#### Home Tab
- Welcome message with app icon
- Recipe stats (total, recent, favorites)
- Quick search bar
- Recently added recipes (cards with thumbnails)
- Random recipe suggestion button

#### Scan Tab
- Scanner preview window
- [Scan] button (large, green)
- Progress bar during scanning
- OCR result preview (editable text area)
- Form fields: Title, Category, Tags
- [Save Recipe] button

#### Browse Recipes Tab
- Search bar at top
- Filter sidebar (category, cuisine, dietary)
- Recipe cards in scrollable grid
- Click card to view full recipe
- Edit/Delete buttons per recipe

#### Ingredient Matcher Tab
- "My Ingredients" input area
- [Add Ingredient] button
- List of entered ingredients (removable tags)
- [Find Recipes] button
- Results with match percentage bars
- Green (100%), Yellow (75%+), Gray (<75%)

#### Grocery List Tab
- Multi-select recipe list
- [Generate List] button
- Organized ingredient list by category
- [Print] and [Export PDF] buttons
- Checkboxes for shopping

### Modal Dialogs
- Recipe Detail View (full screen overlay)
- Scanner Settings
- App Settings (theme, database location)
- About Dialog

---

## 🚀 Future Enhancements (Phase 2+)

### Optional Paid Features (if desired later)
- [ ] OpenAI integration for better parsing ($1-5 total)
- [ ] Nutrition facts estimation (via API)
- [ ] Meal planning calendar
- [ ] Recipe scaling calculator
- [ ] Cloud backup (Dropbox/Google Drive)
- [ ] Mobile app companion
- [ ] Recipe sharing with friends
- [ ] Voice-activated search
- [ ] Barcode scanning for pantry items

### Free Enhancements
- [ ] Recipe rating system
- [ ] Favorite recipes
- [ ] Recipe notes & modifications
- [ ] Print with photos
- [ ] Cooking timer integration
- [ ] Unit conversion calculator
- [ ] Recipe duplication detection
- [ ] Seasonal recipe suggestions

---

## 📖 User Guide (To Be Created)

### Getting Started
1. Install dependencies
2. Configure scanner
3. Scan first recipe
4. Review OCR results
5. Save to database
6. Search and enjoy!

### Best Practices
- Scan recipes on plain white background
- Ensure good lighting
- Review OCR text before saving
- Tag recipes for easier searching
- Keep pantry list updated

---

## 🐛 Known Limitations

1. **OCR Accuracy**: Handwritten recipes may not scan well (use manual entry)
2. **Scanner Compatibility**: Requires Windows WIA-compatible scanner
3. **Offline Only**: No cloud sync in free version
4. **Parsing Rules**: May need manual correction for unusual recipe formats
5. **Ingredient Matching**: Exact text match only (no synonyms in free version)

---

## ✅ Success Criteria

- [ ] Successfully scan and import 10 recipes
- [ ] Search recipes by ingredient with 90%+ accuracy
- [ ] Generate grocery list for 5 recipes
- [ ] Print grocery list in organized format
- [ ] Complete recipe in < 2 minutes (scan to save)
- [ ] User-friendly interface (no coding knowledge needed)

---

## 📞 Support & Documentation

- GitHub Issues for bug reports
- README.md for quick start guide
- In-app help tooltips
- Example recipes included

---

**Last Updated**: October 31, 2025
**Version**: 1.0 (Free Edition)
**Status**: ✅ Plan Complete - Ready to Build
