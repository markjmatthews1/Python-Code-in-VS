r"""
Module: dividend_loader.py
Author: Mark
Created: [Insert Date]
Purpose: Load and clean dividend data from Schwab and E*TRADE files
Location: C:\Python_Projects\DividendTrackerApp\modules\dividend_loader.py
"""

import pandas as pd
import os

# ------------------------- Configuration Section -------------------------
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DATA_DIR = os.path.abspath(DATA_DIR)
SUPPORTED_FORMATS = [".csv", ".xlsx"]

# ------------------------- Function: Load File -------------------------
def load_dividend_file(filename):
    full_path = os.path.join(DATA_DIR, filename)
    
    # Load based on file type
    if filename.endswith(".csv"):
        df = pd.read_csv(full_path)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(full_path, header=3)
    else:
        raise ValueError(f"Unsupported file format: {filename}")

    # Clean headers
    df.columns = [col.strip() for col in df.columns]

    # Replace 0.0, NaN, etc. with blanks
    df = df.replace({pd.NA: '', 'NaN': '', 'nan': '', 0.0: '', 0: '', None: ''})

    # Parse dates cleanly
    for col in df.columns:
        if "date" in col.lower():
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime('%Y-%m-%d').fillna('')

    # Filter to dividend entries only
    df = df[df["TransactionType"].str.lower() == "dividend"].copy()

    # Add contextual columns
    df["Account Type"] = "E*TRADE IRA"  # manually tagged for now
    df["Source"] = "E*TRADE"
    df["Notes"] = "Regular Dividend"

    return df

# ------------------------- Function: List Files in Data Directory -------------------------
def list_available_files():
    """
    Lists all dividend-related files in the data folder that match supported formats.
    """
    files = os.listdir(DATA_DIR)
    return [f for f in files if any(f.endswith(ext) for ext in SUPPORTED_FORMATS)]

# ------------------------- Debug Mode -------------------------
if __name__ == "__main__":
    print("Available dividend files:")
    for file in list_available_files():
        print(" -", file)

    if list_available_files():
        sample_file = list_available_files()[0]
        print(f"\nPreviewing cleaned contents of: {sample_file}")
        preview_df = load_dividend_file(sample_file)
        print(preview_df.head())
    else:
        print("\nNo files found in data folder.")