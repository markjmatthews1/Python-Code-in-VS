
import pandas as pd
import os

csv_path = "historical_data.csv"

# 1. Simulate appending new data (out of order)
new_rows = [
    {"Datetime": "2025-06-13 10:01", "Ticker": "AGQ", "Open": 48.5, "High": 48.6, "Low": 48.4, "Close": 48.55, "Volume": 1000},
    {"Datetime": "2025-06-13 09:59", "Ticker": "AGQ", "Open": 48.3, "High": 48.4, "Low": 48.2, "Close": 48.35, "Volume": 800},
    {"Datetime": "2025-06-13 10:00", "Ticker": "AGQ", "Open": 48.4, "High": 48.5, "Low": 48.3, "Close": 48.45, "Volume": 900},
]

new_df = pd.DataFrame(new_rows)

# Append new rows to the CSV (simulate real-time appending)
file_exists = os.path.isfile(csv_path)
new_df.to_csv(
    csv_path,
    mode="a",
    header=not file_exists,
    index=False
)
print("✅ Appended new rows to historical_data.csv (possibly out of order).")

# 2. Now reload, sort, and overwrite the file to ensure chronological order
#df = pd.read_csv(csv_path)
#df["Datetime"] = pd.to_datetime(df["Datetime"])
#df = df.sort_values(by=["Ticker", "Datetime"])
#df["Datetime"] = df["Datetime"].dt.strftime("%Y-%m-%d %H:%M")
#df.to_csv(csv_path, index=False)
#print("✅ Sorted and saved historical_data.csv in chronological order.")