import os

# Install all dependencies at once
packages = [
    "requests",
    "requests_oauthlib",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "etrade_python_client",
    "alpha_vantage polygon-api-client matplotlib scikit-learn",
    "gspread",
    "gsprread oauth2client",
    "gtts",
    "Dash",
    "yfinance",
    "pyetrade",
    "plotly",
    "ipython",
    "msal",
    "pandas-ta",
    "soundfile",
    "playsound==1.2.2",
    "schedule",
    "pyngrok",
    "python-dotenv",
    "etrade_auth",
    "rauth",
    "psutil",
    "newspaper3k",
    "beautifulsoup4",
    "Sounddevice",
    "textblob vaderSentiment",
    "lxml_html_clean",
    "html5lib",
    "openpyxl",
    "pyttsx3",
    "stockanalysis-scraper"
]

# Run pip install for each package
for package in packages:
    os.system(f"pip install {package}")
