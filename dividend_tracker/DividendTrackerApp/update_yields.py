import pandas as pd
from datetime import datetime

# Known dividend yields from E*TRADE screenshot
yields = {
    'ABR': 10.71, 'ACP': 15.60, 'AGNC': 15.19, 'ARI': 10.22, 'BITO': 53.41,
    'EIC': 12.26, 'MORT': 12.56, 'OFS': 16.39, 'PDI': 13.77, 'QDTE': 8.24,
    'QYLD': 12.52, 'RYLD': 13.10, 'NHS': 16.0, 'JEPI': 8.0, 'JEPQ': 9.0
}

df = pd.read_excel('outputs/Dividends_2025.xlsx')
backup = f'outputs/Dividends_2025_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
df.to_excel(backup, index=False)

for index, row in df.iterrows():
    ticker = str(row['Ticker']).upper().strip()
    if ticker in yields:
        yield_val = yields[ticker]
        df.at[index, '08-02-2025'] = yield_val
        df.at[index, '07-28-2025'] = yield_val
        df.at[index, 'Beginning Dividend Yield'] = yield_val

df.to_excel('outputs/Dividends_2025.xlsx', index=False)
print("Yield data updated!")
