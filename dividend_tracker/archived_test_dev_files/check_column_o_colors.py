import openpyxl
import os

def check_column_o_colors():
    """Check background colors used in Column O"""
    file_path = r"C:\Users\mjmat\Python Code in VS\Historical Yield Data.xlsx"
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return
    
    try:
        wb = openpyxl.load_workbook(file_path)
        ws = wb["Accounts Div historical yield"]
        
        print("COLUMN O BACKGROUND COLORS:")
        print("=" * 40)
        
        # Check first 50 rows for Column O colors
        for row in range(1, 51):
            cell = ws.cell(row=row, column=15)  # Column O
            if cell.value:
                bg_color = cell.fill.start_color.rgb if cell.fill.start_color else "None"
                print(f"Row {row}: {cell.value} -> BG Color: {bg_color}")
        
        wb.close()
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    check_column_o_colors()