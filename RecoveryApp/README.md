# RecoveryApp

A new application built using the existing authentication infrastructure from the Python Code in VS directory.

## Directory Structure

```
RecoveryApp/
├── __init__.py           # Package initialization
├── app.py               # Main application entry point
├── config.json          # Application configuration
├── README.md           # This file
├── auth/               # Authentication modules
│   ├── __init__.py
│   └── auth_manager.py  # Wrapper for existing auth systems
├── gui/                # GUI components
│   ├── __init__.py
│   └── main_gui.py     # Main GUI interface
└── utils/              # Utility modules
    ├── __init__.py
    └── ui_utils.py     # UI styling and components
```

## Features

- Uses existing auth renewal apps from parent directory
- Colorful GUI interface with Arial 12 font standard
- Modular design for easy expansion
- Integrated authentication for E*Trade, FMP, and Schwab APIs

## Usage

Run the application:
```bash
python app.py
```

## Authentication

The app automatically uses existing authentication tokens and keys from the parent directory's auth renewal systems.