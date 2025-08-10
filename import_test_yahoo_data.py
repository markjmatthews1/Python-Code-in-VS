import yfinance as yf
print(yf.download("LABU", period="1d", interval="1m").tail())