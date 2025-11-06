# 🚀 How to Launch the Trade Diagnostic Tool

## Quick Reference

### ⚡ **Fastest Methods**

1. **Double-click the batch file**
   - File: `launch_trade_diagnostic.bat`
   - Location: `weeklypay_rotation_app` folder
   - Just double-click and it opens!

2. **Desktop Shortcut** (Recommended!)
   - Run `create_desktop_shortcut.bat` once
   - Then just double-click the desktop icon
   - Most convenient for daily use!

---

## 📁 **All Launch Methods**

### Method 1: Batch File in Folder
```
Location: C:\Users\mjmat\Python Code in VS\weeklypay_rotation_app\
File: launch_trade_diagnostic.bat

Steps:
1. Open File Explorer
2. Navigate to weeklypay_rotation_app folder
3. Double-click "launch_trade_diagnostic.bat"
```

---

### Method 2: Create Desktop Shortcut (One-time setup)
```
Location: C:\Users\mjmat\Python Code in VS\weeklypay_rotation_app\
File: create_desktop_shortcut.bat

Steps:
1. Navigate to weeklypay_rotation_app folder
2. Double-click "create_desktop_shortcut.bat"
3. A shortcut appears on your desktop
4. From now on, just double-click the desktop icon!
```

**Desktop shortcut features:**
- ✅ One-click access
- ✅ No need to navigate folders
- ✅ Launches from anywhere
- ✅ Professional icon

---

### Method 3: Command Line
```powershell
# From main directory:
python weeklypay_rotation_app\trade_diagnostic_tool.py

# Or navigate to folder first:
cd weeklypay_rotation_app
python trade_diagnostic_tool.py
```

---

### Method 4: VS Code
```
1. Open trade_diagnostic_tool.py in VS Code
2. Press F5 (or click Run → Start Debugging)
   OR
3. Right-click in the file
4. Select "Run Python File in Terminal"
```

---

### Method 5: Python Directly
```powershell
# Full path method (works from anywhere):
python "C:\Users\mjmat\Python Code in VS\weeklypay_rotation_app\trade_diagnostic_tool.py"
```

---

## 🎯 **Recommended Setup**

For easiest daily access:

1. **Run the desktop shortcut creator** (one-time):
   - Double-click `create_desktop_shortcut.bat`
   - Shortcut appears on desktop

2. **From now on**:
   - Just double-click the desktop shortcut
   - Tool opens instantly!

---

## 📂 **File Locations Reference**

```
Python Code in VS/
└── weeklypay_rotation_app/
    ├── trade_diagnostic_tool.py          ← Main tool
    ├── launch_trade_diagnostic.bat       ← Quick launcher
    ├── create_desktop_shortcut.bat       ← Shortcut creator
    ├── weeklypay_trades.csv              ← Your data
    ├── TRADE_EDIT_GUIDE.md              ← Usage guide
    └── EDIT_FEATURE_SUMMARY.md          ← Feature docs
```

---

## 🔧 **Troubleshooting**

### "Python not found" error
Make sure Python is in your PATH, or use full path:
```powershell
C:\Path\To\Python\python.exe weeklypay_rotation_app\trade_diagnostic_tool.py
```

### Batch file doesn't work
1. Right-click `launch_trade_diagnostic.bat`
2. Select "Edit"
3. Check the Python command is correct

### Desktop shortcut fails to create
1. Right-click `create_desktop_shortcut.bat`
2. Select "Run as Administrator"
3. Try again

---

## 💡 **Pro Tips**

### Pin to Taskbar (Windows)
1. Create desktop shortcut first
2. Drag shortcut to taskbar
3. Now it's always one click away!

### Add to Start Menu
1. Press Windows key
2. Type "Trade" or "WeeklyPay"
3. If shortcut is on desktop, it will appear

### Create Folder Bookmark
In File Explorer:
1. Navigate to `weeklypay_rotation_app`
2. Drag folder to "Quick Access"
3. Batch file always accessible

---

## 🎬 **Quick Start**

**First Time Setup:**
1. Double-click `create_desktop_shortcut.bat`
2. ✅ Desktop shortcut created!

**Every Time After:**
1. Double-click desktop shortcut
2. Tool opens!
3. View/Add/Edit/Delete trades
4. Done!

---

## 📞 **Need Help?**

All files are in: `C:\Users\mjmat\Python Code in VS\weeklypay_rotation_app\`

The tool requires:
- ✅ Python installed
- ✅ pandas library (`pip install pandas`)
- ✅ tkinter (included with Python)

If you can run the Streamlit dashboard, you can run this tool!
