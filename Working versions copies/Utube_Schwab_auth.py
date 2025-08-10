import requests
import webbrowser
from flask import Flask, request, redirect, Response
import base64

# ================== CONFIGURATION =====================
APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"
REDIRECT_URL = "https://127.0.0.1:5000/callback"
AUTH_URL = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={APP_KEY}&redirect_uri={REDIRECT_URL}"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"

app = Flask(__name__)

# ================== FLASK ROUTES ======================
@app.route("/callback")  
def auth_callback():
    """Handles OAuth callback and exchanges authorization code for tokens."""
    auth_code = request.args.get("code")
    if auth_code:
        print(f"🔍 Received Authorization Code: {auth_code}")
        return exchange_for_tokens(auth_code)
    else:
        return Response("Error: No authorization code provided.", status=400)

@app.route("/login")
def login():
    """Redirects user to Schwab's OAuth authentication URL."""
    return redirect(AUTH_URL, code=302)

# ================== TOKEN EXCHANGE ======================
def exchange_for_tokens(auth_code):
    """Exchanges authorization code for tokens."""
    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()

    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, headers=headers, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URL
    })

    try:
        token_info = response.json()
        print("✅ Tokens received:", token_info)
        return Response("Authorization successful!", status=200)
    except requests.exceptions.JSONDecodeError:
        return Response("Error decoding token response!", status=500)

# ================== MAIN =============================
def main():
    print("🚀 Starting Flask server...")
    webbrowser.open(AUTH_URL)
    app.run(host="127.0.0.1", port=5000, ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem"))

if __name__ == "__main__":
    main()