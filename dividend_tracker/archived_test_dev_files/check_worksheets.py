import openpyxl

def check_worksheets():
    file_path = r"C:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp\outputs\Dividends_2025.xlsx"
    
    try:
        wb = openpyxl.load_workbook(file_path)
        print("Available worksheets:")
        for sheet_name in wb.sheetnames:
            print(f"  - {sheet_name}")
        wb.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_worksheets()