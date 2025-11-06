import pandas as pd
from collections import Counter

fn = r"c:\Users\mjmat\Python Code in VS\historical_data.csv"
print('Reading', fn)
df = pd.read_csv(fn)
print('Rows:', len(df))
if 'Datetime' in df.columns and 'Ticker' in df.columns:
    dup_mask = df.duplicated(subset=['Datetime','Ticker'], keep=False)
    print('Duplicate rows (keep=False):', dup_mask.sum())
    # show counts per (Datetime,Ticker)
    counts = df.groupby(['Datetime','Ticker']).size().reset_index(name='count')
    dup_counts = counts[counts['count']>1].sort_values('count', ascending=False)
    print('Distinct duplicate keys:', len(dup_counts))
    print('Top duplicate keys:')
    print(dup_counts.head(10).to_string(index=False))
    # show sample duplicates for AMD
    amd_dup = df[(df['Ticker']=='AMD') & (dup_mask)]
    if not amd_dup.empty:
        print('\nSample AMD duplicate rows:')
        print(amd_dup.head(40).to_csv(index=False))
    else:
        print('No AMD duplicates found')
else:
    print('Required columns missing')
