import openpyxl

# Load the workbook and Portfolio Summary sheet
wb = openpyxl.load_workbook('outputs/Dividends_2025.xlsx')
ws = wb['Portfolio Summary']

print("PORTFOLIO SUMMARY SHEET ANALYSIS")
print("=" * 40)

print("\nFirst 20 rows, columns A-F:")
for i in range(1, 21):
    row_data = []
    for j in range(1, 7):
        cell_value = ws.cell(i, j).value
        if cell_value is None:
            row_data.append("None")
        elif isinstance(cell_value, (int, float)):
            row_data.append(f"{cell_value:.2f}")
        else:
            row_data.append(str(cell_value)[:30])
    print(f"Row {i:2d}: {row_data}")

wb.close()