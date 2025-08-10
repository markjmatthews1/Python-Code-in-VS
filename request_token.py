from schwab.auth import client_from_login_flow

if __name__ == "__main__":
    c = client_from_login_flow(
        api_key="JkBlFHJRnXkrYzansLzRinYXZ4u6vyjS",
        app_secret="ycX2EDU8Qhkt4L7s",
        callback_url="https://127.0.0.1:8132",
        token_path="/tmp/token.json"
    )


