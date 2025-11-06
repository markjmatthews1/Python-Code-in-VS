# 🍳 Recipe Scanner Pro

A free, standalone desktop application for scanning, organizing, and managing your recipe collection with smart ingredient matching and grocery list generation.

## ✨ Features

- **📷 Scan Recipes**: Use your HP scanner to digitize paper recipes
- **🔍 OCR Processing**: Automatic text extraction from scanned images
- **📚 Recipe Database**: Organize and search your recipe collection
- **🎯 Ingredient Matching**: Find recipes based on ingredients you have
- **📝 Grocery Lists**: Generate shopping lists from selected recipes
- **🎨 Modern GUI**: Colorful, user-friendly interface
- **💾 100% Free**: No subscriptions, all data stored locally

## 🚀 Installation

### Prerequisites

1. **Python 3.10 or higher**
   - Download from: https://www.python.org/downloads/

2. **Tesseract OCR**
   - Download from: https://github.com/UB-Mannheim/tesseract/wiki
   - Install to: `C:\Program Files\Tesseract-OCR\`
   - Add to system PATH

3. **HP Scanner** (connected and working)

### Setup Steps

1. Clone or download this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

## 📖 Usage Guide

### Scanning a Recipe

1. Place recipe on scanner
2. Click **Scan** tab
3. Click **Start Scan** button
4. Review OCR extracted text
5. Edit if needed
6. Click **Save Recipe**

### Finding Recipes by Ingredients

1. Click **Match** tab
2. Enter ingredients you have
3. Click **Find Recipes**
4. View matches sorted by percentage

### Creating a Grocery List

1. Click **List** tab
2. Select recipes for the week
3. Click **Generate List**
4. Print or export to PDF

## 🔧 Building Executable

To create a standalone `.exe` file:

```bash
pyinstaller --onefile --windowed --icon=icon.ico --name="RecipeScannerPro" app.py
```

The executable will be in the `dist` folder.

## 📁 Data Location

- **Database**: `data/recipes.db`
- **Scanned Images**: `data/scanned_images/`
- **Backups**: `data/backups/`

## 🎨 Themes

Toggle between light and dark themes using the moon icon in the bottom right.

## 🐛 Troubleshooting

**Scanner not detected?**
- Ensure scanner is connected and drivers installed
- Check Windows Device Manager

**OCR not working?**
- Verify Tesseract is installed
- Check PATH environment variable

**Blurry scans?**
- Clean scanner glass
- Ensure recipe is flat on scanner
- Adjust scanner resolution in settings

## 📞 Support

For issues or feature requests, please open an issue on GitHub.

## 📜 License

MIT License - Free to use and modify

## 🙏 Credits

- Built with CustomTkinter
- OCR powered by Tesseract
- Icons from various free sources

---

**Version**: 1.0  
**Last Updated**: October 31, 2025
