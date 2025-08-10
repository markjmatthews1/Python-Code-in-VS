import requests

resp = requests.get("http://127.0.0.1:4040/api/tunnels")
for tunnel in resp.json()["tunnels"]:
    print("Public URL:", tunnel["public_url"])
    print("Forwards to:", tunnel["config"]["addr"])