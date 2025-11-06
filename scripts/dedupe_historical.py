import os
import shutil
from datetime import datetime
import pandas as pd

INFILE = r"c:\Users\mjmat\Python Code in VS\historical_data.csv"
# create backup
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = INFILE + ".backup_" + stamp
shutil.copy2(INFILE, BACKUP)
print(f"Backup created: {BACKUP}")

# read
df = pd.read_csv(INFILE)
print(f"Rows read: {len(df)}")

# normalize Datetime
df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
na_dates = df['Datetime'].isna().sum()
if na_dates:
    print(f"Warning: {na_dates} rows had unparsable Datetime and will be dropped")
    df = df.dropna(subset=['Datetime'])

# floor to minute and format
df['Datetime'] = df['Datetime'].dt.floor('T')
# ensure ticker is clean
if 'Ticker' in df.columns:
    df['Ticker'] = df['Ticker'].astype(str).str.strip()

# format Datetime column consistently
df['Datetime'] = df['Datetime'].dt.strftime('%Y-%m-%d %H:%M')

before = len(df)
# sort then drop duplicates by Datetime+Ticker keeping last
df = df.sort_values(['Ticker', 'Datetime'])
df = df.drop_duplicates(subset=['Datetime', 'Ticker'], keep='last').reset_index(drop=True)
after = len(df)
removed = before - after
print(f"Rows before: {before}, after dedupe: {after}, removed: {removed}")

# atomic write
TMP = INFILE + ".tmp"
cols = ['Datetime','Ticker','Open','High','Low','Close','Volume']
# ensure columns order if present
cols_present = [c for c in cols if c in df.columns]
df.to_csv(TMP, index=False, columns=cols_present)
# replace
os.replace(TMP, INFILE)
print(f"Deduplicated file written to: {INFILE}")

# show sample for BITU if present
if 'Ticker' in df.columns:
    subset = df[df['Ticker'] == 'BITU']
    if not subset.empty:
        print("BITU sample rows after dedupe:")
        print(subset.head(20).to_csv(index=False))
    else:
        print("No BITU rows found after dedupe.")
