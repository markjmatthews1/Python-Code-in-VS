from flask import Flask

app = Flask(__name__)

@app.route("/callback")
def callback():
    return "Flask/ngrok test: callback is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

    # === CONFIGURATION ===
SCHWAB_CLIENT_ID = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"  # <-- Replace with your Schwab App Key
SCHWAB_CLIENT_SECRET = "h9YybKHnDVoDM1Jw"               # <-- Replace with your Schwab App Secret
