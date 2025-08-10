import pandas as pd

for fname in ["scored_my_holdings.csv", "scored_candidates.csv"]:
    df = pd.read_csv(fname)
    for col in ["Ex-Dividend Date", "Payout Date"]:
        if col not in df.columns:
            df[col] = ""
    df.to_csv(fname, index=False)