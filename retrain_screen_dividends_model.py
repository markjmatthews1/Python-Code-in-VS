import pandas as pd
from screen_dividends import train_continuity_model

# Load your labeled data (holdings and/or candidates)
df_holdings = pd.read_csv("scored_my_holdings.csv")
df_candidates = pd.read_csv("scored_candidates.csv")

# Combine if you want to use both as training data
df_train = pd.concat([df_holdings, df_candidates], ignore_index=True)

# Retrain the model and save it
train_continuity_model(df_train, model_path="div_continuity_model.joblib")