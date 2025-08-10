from flask import Flask, render_template_string
from ngrok_manager import get_ngrok_status
import time

app = Flask(__name__)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ngrok Tunnel Status</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial; background: #222244; color: #fff; text-align: center; }
        .status { font-size: 2em; margin-top: 40px; }
        .live { color: #00FF00; }
        .down { color: #FF4444; }
        .url { font-size: 1.2em; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>ngrok Tunnel Status</h1>
    {% if url %}
        <div class="url">Current ngrok URL:<br><b>{{ url }}</b></div>
        <div class="status {{ 'live' if is_live else 'down' }}">
            {{ "LIVE ✅" if is_live else "OFFLINE ❌" }}
        </div>
    {% else %}
        <div class="status down">No ngrok URL found.</div>
    {% endif %}
    <p style="margin-top:40px;">Auto-refreshes every 5 seconds.</p>
</body>
</html>
"""

@app.route("/")
def status():
    url, is_live = get_ngrok_status()
    return render_template_string(TEMPLATE, url=url, is_live=is_live)

if __name__ == "__main__":
    app.run(port=5000, debug=False)