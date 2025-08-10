import os
from pyngrok import ngrok
import requests

NGROK_URL_FILE = "ngrok_url.txt"
NGROK_PORT = 5000  # Change if your Flask OAuth callback server uses a different port

def start_ngrok_once(port=NGROK_PORT):
    """
    Starts ngrok only if not already running and saves the public URL to a file.
    Checks if the tunnel is live before reusing.
    """
    if os.path.exists(NGROK_URL_FILE):
        with open(NGROK_URL_FILE, "r") as f:
            url = f.read().strip()
            # Check if the tunnel is live
            try:
                resp = requests.get(url + "/callback", timeout=3)
                # Any response (even 404) means the tunnel is up
                print(f"[ngrok_manager] Reusing existing ngrok URL: {url}")
                return url
            except Exception:
                print("[ngrok_manager] Old ngrok URL is dead, starting a new tunnel...")
    public_url = ngrok.connect(5000, "http", domain="schwab.ngrok.pro").public_url
    if public_url.startswith("http://"):
        public_url = public_url.replace("http://", "https://")
    with open(NGROK_URL_FILE, "w") as f:
        f.write(public_url)
    print(f"[ngrok_manager] Started new ngrok tunnel: {public_url}")
    return public_url

def is_ngrok_tunnel_live(public_url):
    try:
        resp = requests.get(f"{public_url}/callback", timeout=5)
        # Accept any 2xx, 3xx, or 4xx response as "live"
        return resp.status_code in range(200, 500)
    except Exception:
        return False

def get_ngrok_url():
    """
    Returns the current ngrok public URL from file.
    """
    if os.path.exists(NGROK_URL_FILE):
        with open(NGROK_URL_FILE, "r") as f:
            return f.read().strip()
    return None

def get_ngrok_status():
    """
    Returns a tuple (url, is_live) for the current ngrok tunnel.
    """
    url = get_ngrok_url()
    if url:
        return url, is_ngrok_tunnel_live(url)
    return None, False

def stop_ngrok():
    """
    Stops all ngrok tunnels and removes the URL file.
    """
    ngrok.kill()
    if os.path.exists(NGROK_URL_FILE):
        os.remove(NGROK_URL_FILE)
    print("[ngrok_manager] Stopped ngrok and cleaned up URL file.")